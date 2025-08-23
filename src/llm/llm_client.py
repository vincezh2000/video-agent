"""LLM client for interacting with language models."""

import os
import json
from typing import Dict, List, Optional, Any
from enum import Enum
import asyncio
from loguru import logger

try:
    import openai
    from openai import AsyncOpenAI
except ImportError:
    logger.warning("OpenAI library not installed. Install with: pip install openai")
    openai = None
    AsyncOpenAI = None


class ModelType(Enum):
    """Available model types."""
    GPT4 = "gpt-4-turbo-preview"
    GPT4_VISION = "gpt-4-vision-preview"
    GPT35_TURBO = "gpt-3.5-turbo"
    GPT35_16K = "gpt-3.5-turbo-16k"


class LLMClient:
    """Client for interacting with Large Language Models."""
    
    def __init__(self, api_key: Optional[str] = None, model: ModelType = ModelType.GPT4):
        """Initialize the LLM client.
        
        Args:
            api_key: OpenAI API key (if not provided, uses environment variable)
            model: Model type to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
        
        if AsyncOpenAI is None:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
            
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model
        self._retry_count = 3
        self._retry_delay = 1.0
        
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.8,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None,
        seed: Optional[int] = None
    ) -> str:
        """Generate a response from the LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            response_format: Optional JSON schema for structured output
            seed: Random seed for reproducibility
            
        Returns:
            Generated text response
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        for attempt in range(self._retry_count):
            try:
                kwargs = {
                    "model": self.model.value,
                    "messages": messages,
                    "temperature": temperature,
                }
                
                if max_tokens:
                    kwargs["max_tokens"] = max_tokens
                if seed is not None:
                    kwargs["seed"] = seed
                if response_format:
                    kwargs["response_format"] = {"type": "json_object"}
                    
                response = await self.client.chat.completions.create(**kwargs)
                
                content = response.choices[0].message.content
                
                # If JSON format requested, validate the response
                if response_format:
                    try:
                        json.loads(content)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON response on attempt {attempt + 1}")
                        if attempt < self._retry_count - 1:
                            await asyncio.sleep(self._retry_delay * (attempt + 1))
                            continue
                        raise
                
                logger.debug(f"LLM generation successful. Model: {self.model.value}, Tokens: {response.usage.total_tokens}")
                return content
                
            except Exception as e:
                logger.error(f"LLM generation failed on attempt {attempt + 1}: {e}")
                if attempt < self._retry_count - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))
                else:
                    raise
                    
    async def generate_with_evaluation(
        self,
        prompt: str,
        evaluation_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.8,
        max_iterations: int = 3
    ) -> tuple[str, float]:
        """Generate content and evaluate it iteratively.
        
        Args:
            prompt: Generation prompt
            evaluation_prompt: Prompt template for evaluation
            system_prompt: System context
            temperature: Sampling temperature
            max_iterations: Maximum refinement iterations
            
        Returns:
            Tuple of (generated content, quality score)
        """
        best_content = ""
        best_score = 0.0
        
        for iteration in range(max_iterations):
            # Generate content
            content = await self.generate(prompt, system_prompt, temperature)
            
            # Evaluate content
            eval_prompt = evaluation_prompt.format(content=content)
            eval_response = await self.generate(
                eval_prompt,
                system_prompt="You are a critical evaluator. Rate quality from 0-1 and provide specific feedback.",
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            try:
                eval_data = json.loads(eval_response)
                score = float(eval_data.get("score", 0))
                feedback = eval_data.get("feedback", "")
                
                logger.info(f"Iteration {iteration + 1}: Score = {score:.2f}")
                
                if score > best_score:
                    best_content = content
                    best_score = score
                
                # If score is good enough, stop iterating
                if score >= 0.85:
                    break
                    
                # Otherwise, refine the prompt with feedback
                prompt = f"{prompt}\n\nPrevious attempt feedback: {feedback}\nPlease improve based on this feedback."
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"Failed to parse evaluation response: {e}")
                continue
                
        return best_content, best_score
    
    async def batch_generate(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        temperature: float = 0.8,
        max_concurrent: int = 5
    ) -> List[str]:
        """Generate responses for multiple prompts concurrently.
        
        Args:
            prompts: List of prompts
            system_prompt: System context
            temperature: Sampling temperature
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of generated responses
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_with_semaphore(prompt: str) -> str:
            async with semaphore:
                return await self.generate(prompt, system_prompt, temperature)
        
        tasks = [generate_with_semaphore(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to generate response for prompt {i}: {result}")
                processed_results.append("")
            else:
                processed_results.append(result)
                
        return processed_results
    
    def switch_model(self, model: ModelType):
        """Switch to a different model.
        
        Args:
            model: New model to use
        """
        self.model = model
        logger.info(f"Switched to model: {model.value}")
        
    async def close(self):
        """Close the client connection."""
        if hasattr(self.client, 'close'):
            await self.client.close()