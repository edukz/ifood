import random
import time
import asyncio
from typing import Optional, Tuple
from playwright.sync_api import Page
from playwright.async_api import Page as AsyncPage


class HumanBehavior:
    """Simula comportamento humano no navegador"""
    
    @staticmethod
    def random_delay(min_seconds: float = 0.1, max_seconds: float = 2.0) -> float:
        """Retorna um delay aleatório"""
        return random.uniform(min_seconds, max_seconds)
    
    @staticmethod
    def typing_delay() -> float:
        """Retorna delay entre teclas (simula digitação humana)"""
        return random.uniform(0.05, 0.2)
    
    @staticmethod
    def random_mouse_movement(page: Page, steps: int = 3):
        """Move o mouse aleatoriamente pela página"""
        viewport = page.viewport_size
        if not viewport:
            return
            
        for _ in range(steps):
            x = random.randint(100, viewport['width'] - 100)
            y = random.randint(100, viewport['height'] - 100)
            
            # Movimento suave do mouse
            page.mouse.move(x, y, steps=random.randint(10, 30))
            time.sleep(HumanBehavior.random_delay(0.1, 0.5))
    
    @staticmethod
    async def async_random_mouse_movement(page: AsyncPage, steps: int = 3):
        """Versão assíncrona do movimento do mouse"""
        viewport = page.viewport_size
        if not viewport:
            return
            
        for _ in range(steps):
            x = random.randint(100, viewport['width'] - 100)
            y = random.randint(100, viewport['height'] - 100)
            
            await page.mouse.move(x, y, steps=random.randint(10, 30))
            await asyncio.sleep(HumanBehavior.random_delay(0.1, 0.5))
    
    @staticmethod
    def random_scroll(page: Page, direction: str = "both"):
        """Faz scroll aleatório na página"""
        viewport = page.viewport_size
        if not viewport:
            return
            
        scroll_amount = random.randint(100, 500)
        
        if direction == "down" or (direction == "both" and random.choice([True, False])):
            page.mouse.wheel(0, scroll_amount)
        else:
            page.mouse.wheel(0, -scroll_amount)
        
        time.sleep(HumanBehavior.random_delay(0.5, 1.5))
    
    @staticmethod
    def human_type(page: Page, selector: str, text: str, clear_first: bool = True):
        """Digita texto de forma mais humana"""
        element = page.locator(selector)
        
        # Clica no elemento
        element.click()
        time.sleep(HumanBehavior.random_delay(0.2, 0.5))
        
        # Limpa o campo se necessário
        if clear_first:
            element.clear()
            time.sleep(HumanBehavior.random_delay(0.1, 0.3))
        
        # Digita caractere por caractere
        for char in text:
            element.type(char)
            time.sleep(HumanBehavior.typing_delay())
            
            # Ocasionalmente faz uma pausa maior
            if random.random() < 0.1:
                time.sleep(HumanBehavior.random_delay(0.3, 0.8))
    
    @staticmethod
    def random_wait():
        """Espera aleatória entre ações"""
        time.sleep(HumanBehavior.random_delay(0.5, 2.0))
    
    @staticmethod
    def simulate_reading_time(text_length: int):
        """Simula tempo de leitura baseado no comprimento do texto"""
        # Assume 200-300 palavras por minuto
        words = text_length / 5  # média de 5 caracteres por palavra
        reading_time = (words / 250) * 60  # segundos
        
        # Adiciona variação aleatória
        variation = random.uniform(0.8, 1.2)
        time.sleep(reading_time * variation)
    
    @staticmethod
    def random_mouse_hover(page: Page, selector: str):
        """Faz hover em um elemento de forma natural"""
        element = page.locator(selector)
        
        if element.count() > 0:
            # Move para perto do elemento primeiro
            box = element.bounding_box()
            if box:
                # Move para uma posição próxima
                nearby_x = box['x'] + random.randint(-50, 50)
                nearby_y = box['y'] + random.randint(-50, 50)
                page.mouse.move(nearby_x, nearby_y, steps=random.randint(5, 15))
                time.sleep(HumanBehavior.random_delay(0.1, 0.3))
                
                # Depois move para o elemento
                element.hover()
                time.sleep(HumanBehavior.random_delay(0.2, 0.8))