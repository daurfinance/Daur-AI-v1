"""
Real Input Control with PyAutoGUI
Полнофункциональное управление вводом - мышь, клавиатура, сенсор
"""

import logging
import time
from typing import Tuple, Optional, List
from enum import Enum
import threading

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logging.warning("PyAutoGUI not available. Install with: pip install pyautogui")

try:
    from pynput.keyboard import Controller as KeyboardController, Key
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    logging.warning("pynput not available. Install with: pip install pynput")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MouseButton(Enum):
    """Кнопки мыши"""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class KeyModifier(Enum):
    """Модификаторы клавиш"""
    CTRL = "ctrl"
    SHIFT = "shift"
    ALT = "alt"
    CMD = "cmd"


class RealInputControl:
    """Реальное управление вводом"""
    
    def __init__(self):
        """Инициализация"""
        if not PYAUTOGUI_AVAILABLE:
            raise ImportError("PyAutoGUI is required. Install with: pip install pyautogui")
        
        self.logger = logging.getLogger(__name__)
        
        # Отключаем failsafe для headless окружения
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.1  # Пауза между командами
        
        # Инициализируем pynput если доступен
        self.keyboard = KeyboardController() if PYNPUT_AVAILABLE else None
        
        self.logger.info("Real Input Control initialized")
    
    # ===== MOUSE OPERATIONS =====
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> bool:
        """
        Переместить мышь
        
        Args:
            x: X координата
            y: Y координата
            duration: Время перемещения в секундах
        
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.moveTo(x, y, duration=duration)
            self.logger.info(f"Mouse moved to: ({x}, {y})")
            return True
        except Exception as e:
            self.logger.error(f"Error moving mouse: {e}")
            return False
    
    def move_mouse_relative(self, dx: int, dy: int, duration: float = 0.5) -> bool:
        """
        Переместить мышь относительно текущей позиции
        
        Args:
            dx: Смещение по X
            dy: Смещение по Y
            duration: Время перемещения в секундах
        
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.moveRel(dx, dy, duration=duration)
            self.logger.info(f"Mouse moved relative: ({dx}, {dy})")
            return True
        except Exception as e:
            self.logger.error(f"Error moving mouse relative: {e}")
            return False
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Получить текущую позицию мыши
        
        Returns:
            Tuple[int, int]: Координаты мыши (x, y)
        """
        try:
            return pyautogui.position()
        except Exception as e:
            self.logger.error(f"Error getting mouse position: {e}")
            return (0, 0)
    
    def click(self, x: int = None, y: int = None, button: str = "left", 
              clicks: int = 1, interval: float = 0.1) -> bool:
        """
        Кликнуть мышью
        
        Args:
            x: X координата (если None, используется текущая позиция)
            y: Y координата (если None, используется текущая позиция)
            button: Кнопка мыши (left, right, middle)
            clicks: Количество кликов
            interval: Интервал между кликами
        
        Returns:
            bool: Успешность операции
        """
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
            else:
                pyautogui.click(clicks=clicks, interval=interval, button=button)
            
            self.logger.info(f"Clicked {clicks} time(s) with {button} button")
            return True
        except Exception as e:
            self.logger.error(f"Error clicking: {e}")
            return False
    
    def double_click(self, x: int = None, y: int = None, interval: float = 0.1) -> bool:
        """
        Двойной клик
        
        Args:
            x: X координата
            y: Y координата
            interval: Интервал между кликами
        
        Returns:
            bool: Успешность операции
        """
        try:
            if x is not None and y is not None:
                pyautogui.doubleClick(x, y, interval=interval)
            else:
                pyautogui.doubleClick(interval=interval)
            
            self.logger.info("Double clicked")
            return True
        except Exception as e:
            self.logger.error(f"Error double clicking: {e}")
            return False
    
    def right_click(self, x: int = None, y: int = None) -> bool:
        """
        Правый клик
        
        Args:
            x: X координата
            y: Y координата
        
        Returns:
            bool: Успешность операции
        """
        try:
            if x is not None and y is not None:
                pyautogui.rightClick(x, y)
            else:
                pyautogui.rightClick()
            
            self.logger.info("Right clicked")
            return True
        except Exception as e:
            self.logger.error(f"Error right clicking: {e}")
            return False
    
    def middle_click(self, x: int = None, y: int = None) -> bool:
        """
        Клик средней кнопкой
        
        Args:
            x: X координата
            y: Y координата
        
        Returns:
            bool: Успешность операции
        """
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, button='middle')
            else:
                pyautogui.click(button='middle')
            
            self.logger.info("Middle clicked")
            return True
        except Exception as e:
            self.logger.error(f"Error middle clicking: {e}")
            return False
    
    def scroll(self, x: int, y: int, clicks: int = 5) -> bool:
        """
        Прокрутить колёсико мыши
        
        Args:
            x: X координата
            y: Y координата
            clicks: Количество прокруток (положительное - вверх, отрицательное - вниз)
        
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.moveTo(x, y)
            pyautogui.scroll(clicks)
            self.logger.info(f"Scrolled {clicks} clicks at ({x}, {y})")
            return True
        except Exception as e:
            self.logger.error(f"Error scrolling: {e}")
            return False
    
    def drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int, 
                      duration: float = 0.5) -> bool:
        """
        Перетащить элемент
        
        Args:
            start_x: Начальная X координата
            start_y: Начальная Y координата
            end_x: Конечная X координата
            end_y: Конечная Y координата
            duration: Время перетаскивания
        
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.moveTo(start_x, start_y)
            pyautogui.mouseDown()
            pyautogui.moveTo(end_x, end_y, duration=duration)
            pyautogui.mouseUp()
            self.logger.info(f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            return True
        except Exception as e:
            self.logger.error(f"Error dragging and dropping: {e}")
            return False
    
    def mouse_down(self, button: str = "left") -> bool:
        """
        Нажать кнопку мыши
        
        Args:
            button: Кнопка мыши
        
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.mouseDown(button=button)
            self.logger.info(f"Mouse button {button} pressed")
            return True
        except Exception as e:
            self.logger.error(f"Error pressing mouse button: {e}")
            return False
    
    def mouse_up(self, button: str = "left") -> bool:
        """
        Отпустить кнопку мыши
        
        Args:
            button: Кнопка мыши
        
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.mouseUp(button=button)
            self.logger.info(f"Mouse button {button} released")
            return True
        except Exception as e:
            self.logger.error(f"Error releasing mouse button: {e}")
            return False
    
    # ===== KEYBOARD OPERATIONS =====
    
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """
        Напечатать текст
        
        Args:
            text: Текст для печати
            interval: Интервал между символами
        
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.typewrite(text, interval=interval)
            self.logger.info(f"Typed text: {text}")
            return True
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
            return False
    
    def write_text(self, text: str) -> bool:
        """
        Написать текст (поддерживает Unicode)
        
        Args:
            text: Текст для написания
        
        Returns:
            bool: Успешность операции
        """
        try:
            if self.keyboard:
                self.keyboard.type(text)
            else:
                pyautogui.typewrite(text)
            
            self.logger.info(f"Wrote text: {text}")
            return True
        except Exception as e:
            self.logger.error(f"Error writing text: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """
        Нажать клавишу
        
        Args:
            key: Название клавиши (enter, space, tab, esc, backspace, delete, etc.)
        
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.press(key)
            self.logger.info(f"Pressed key: {key}")
            return True
        except Exception as e:
            self.logger.error(f"Error pressing key: {e}")
            return False
    
    def key_down(self, key: str) -> bool:
        """
        Нажать клавишу (без отпускания)
        
        Args:
            key: Название клавиши
        
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.keyDown(key)
            self.logger.info(f"Key {key} pressed down")
            return True
        except Exception as e:
            self.logger.error(f"Error pressing key down: {e}")
            return False
    
    def key_up(self, key: str) -> bool:
        """
        Отпустить клавишу
        
        Args:
            key: Название клавиши
        
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.keyUp(key)
            self.logger.info(f"Key {key} released")
            return True
        except Exception as e:
            self.logger.error(f"Error releasing key: {e}")
            return False
    
    def hotkey(self, *keys) -> bool:
        """
        Нажать комбинацию клавиш
        
        Args:
            *keys: Клавиши для комбинации (например: 'ctrl', 'c')
        
        Returns:
            bool: Успешность операции
        """
        try:
            pyautogui.hotkey(*keys)
            self.logger.info(f"Hotkey pressed: {' + '.join(keys)}")
            return True
        except Exception as e:
            self.logger.error(f"Error pressing hotkey: {e}")
            return False
    
    def copy(self) -> bool:
        """Скопировать (Ctrl+C)"""
        return self.hotkey('ctrl', 'c')
    
    def paste(self) -> bool:
        """Вставить (Ctrl+V)"""
        return self.hotkey('ctrl', 'v')
    
    def cut(self) -> bool:
        """Вырезать (Ctrl+X)"""
        return self.hotkey('ctrl', 'x')
    
    def select_all(self) -> bool:
        """Выбрать всё (Ctrl+A)"""
        return self.hotkey('ctrl', 'a')
    
    def undo(self) -> bool:
        """Отменить (Ctrl+Z)"""
        return self.hotkey('ctrl', 'z')
    
    def redo(self) -> bool:
        """Повторить (Ctrl+Y)"""
        return self.hotkey('ctrl', 'y')
    
    def save(self) -> bool:
        """Сохранить (Ctrl+S)"""
        return self.hotkey('ctrl', 's')
    
    def find(self) -> bool:
        """Найти (Ctrl+F)"""
        return self.hotkey('ctrl', 'f')
    
    def close_window(self) -> bool:
        """Закрыть окно (Ctrl+W)"""
        return self.hotkey('ctrl', 'w')
    
    def close_application(self) -> bool:
        """Закрыть приложение (Ctrl+Q)"""
        return self.hotkey('ctrl', 'q')
    
    def alt_tab(self) -> bool:
        """Переключить окна (Alt+Tab)"""
        return self.hotkey('alt', 'tab')
    
    def enter(self) -> bool:
        """Нажать Enter"""
        return self.press_key('enter')
    
    def escape(self) -> bool:
        """Нажать Escape"""
        return self.press_key('esc')
    
    def space(self) -> bool:
        """Нажать Space"""
        return self.press_key('space')
    
    def tab(self) -> bool:
        """Нажать Tab"""
        return self.press_key('tab')
    
    def backspace(self, count: int = 1) -> bool:
        """
        Нажать Backspace
        
        Args:
            count: Количество раз
        
        Returns:
            bool: Успешность операции
        """
        try:
            for _ in range(count):
                self.press_key('backspace')
            return True
        except Exception as e:
            self.logger.error(f"Error pressing backspace: {e}")
            return False
    
    def delete(self, count: int = 1) -> bool:
        """
        Нажать Delete
        
        Args:
            count: Количество раз
        
        Returns:
            bool: Успешность операции
        """
        try:
            for _ in range(count):
                self.press_key('delete')
            return True
        except Exception as e:
            self.logger.error(f"Error pressing delete: {e}")
            return False
    
    # ===== UTILITY METHODS =====
    
    def sleep(self, seconds: float) -> bool:
        """
        Пауза
        
        Args:
            seconds: Количество секунд
        
        Returns:
            bool: Успешность операции
        """
        try:
            time.sleep(seconds)
            self.logger.info(f"Slept for {seconds} seconds")
            return True
        except Exception as e:
            self.logger.error(f"Error sleeping: {e}")
            return False
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Получить размер экрана
        
        Returns:
            Tuple[int, int]: Ширина и высота экрана
        """
        try:
            return pyautogui.size()
        except Exception as e:
            self.logger.error(f"Error getting screen size: {e}")
            return (0, 0)
    
    def locate_image(self, image_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        Найти изображение на экране
        
        Args:
            image_path: Путь к изображению
            confidence: Уровень уверенности (0-1)
        
        Returns:
            Optional[Tuple[int, int]]: Координаты центра найденного изображения или None
        """
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                self.logger.info(f"Image found at: {center}")
                return center
            else:
                self.logger.warning(f"Image not found: {image_path}")
                return None
        except Exception as e:
            self.logger.error(f"Error locating image: {e}")
            return None
    
    def click_image(self, image_path: str, confidence: float = 0.8) -> bool:
        """
        Найти и кликнуть на изображение
        
        Args:
            image_path: Путь к изображению
            confidence: Уровень уверенности
        
        Returns:
            bool: Успешность операции
        """
        try:
            location = self.locate_image(image_path, confidence)
            if location:
                self.click(location[0], location[1])
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error clicking image: {e}")
            return False

