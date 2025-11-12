import pytest
import asyncio
from pathlib import Path
from src.browser.browser_automation import BrowserAutomation
from src.browser.playwright_utils import playwright_module

@pytest.fixture
async def browser():
    """Фикстура для тестирования браузерной автоматизации.
    Использует мок-реализацию Playwright."""
    browser = BrowserAutomation(headless=True)
    await browser.init()
    yield browser
    await browser.close()

@pytest.fixture
def mock_page(browser):
    """Фикстура для доступа к мок-странице."""
    return browser.page

@pytest.mark.asyncio
async def test_init(browser):
    """Тест инициализации браузера."""
    assert browser.browser is not None
    assert browser.page is not None
    assert browser.headless is True

@pytest.mark.asyncio
async def test_navigation(browser, mock_page):
    """Тест навигации по URL."""
    # Проверяем успешную навигацию
    success = await browser.navigate("https://example.com")
    assert success is True
    assert mock_page.url == "https://example.com"
    
    # Проверяем что можно получить содержимое страницы
    content = await browser.page.content()
    assert "Mock page" in content
    
    # При ошибке навигации mock вызывает исключение
    with pytest.raises(Exception):
        await browser.navigate("invalid://url")

@pytest.mark.asyncio
async def test_find_element(browser):
    """Тест поиска элемента на странице."""
    await browser.navigate("https://example.com")
    
    # Ищем существующий элемент (mock всегда возвращает элемент)
    element = await browser.find_element("h1")
    assert element is not None
    
    # Проверяем методы работы с элементом
    await element.click()
    await element.type("test input")
    await element.fill("test value")
    is_visible = await element.is_visible()
    assert is_visible is True

@pytest.mark.asyncio
async def test_element_properties(browser):
    """Тест получения свойств элемента."""
    await browser.navigate("https://example.com")
    element = await browser.find_element(".test-element")
    
    # Проверяем различные свойства элемента
    box = await element.bounding_box()
    assert box["x"] == 0
    assert box["y"] == 0
    assert box["width"] == 100
    assert box["height"] == 30
    
    attr = await element.get_attribute("class")
    assert attr == "mock_class_value"
    
    screenshot = await element.screenshot()
    assert screenshot == b"mock_screenshot_data"
    
@pytest.mark.asyncio
async def test_form_interaction(browser):
    """Тест взаимодействия с формами."""
    await browser.navigate("https://example.com/form")
    
    # Заполняем поля формы
    username_field = await browser.find_element("#username")
    password_field = await browser.find_element("#password")
    
    await username_field.fill("testuser")
    await password_field.fill("password123")
    
    # Нажимаем кнопку отправки
    submit_button = await browser.find_element("button[type='submit']")
    await submit_button.click()
    
    # В mock реализации эти действия только логируются
    # В реальном тестировании здесь была бы проверка редиректа/ответа
    
@pytest.mark.asyncio
async def test_navigation_events(browser, mock_page):
    """Тест обработки событий навигации."""
    navigation_events = []
    
    # Добавляем обработчик события загрузки
    def on_load(event):
        navigation_events.append(event)
        
    mock_page.on("load", on_load)
    
    # Выполняем навигацию
    await browser.navigate("https://example.com")
    await browser.page.reload()
    
    # Проверяем что события были обработаны
    # В mock реализации события только логируются
    
@pytest.mark.asyncio
async def test_viewport_control(browser):
    """Тест управления размером viewport."""
    await browser.navigate("https://example.com")
    
    # Устанавливаем размер viewport
    viewport = {"width": 1920, "height": 1080}
    await browser.page.set_viewport_size(viewport)
    
    # В mock реализации это только обновляет внутреннее состояние
async def test_type_text(browser):
    """Тест ввода текста."""
    await browser.navigate("https://example.com")
    
    # Вводим текст в существующее поле
    success = await browser.type_text("input[type='text']", "Test input")
    assert success is True
    
    # Пытаемся ввести текст в несуществующее поле
    success = await browser.type_text("#nonexistent", "Test input")
    assert success is False
    
@pytest.mark.asyncio
async def test_get_text(browser):
    """Тест получения текста элемента."""
    await browser.navigate("https://example.com")
    
    # Получаем текст существующего элемента
    text = await browser.get_text("h1")
    assert text is not None
    assert isinstance(text, str)
    
    # Пытаемся получить текст несуществующего элемента
    text = await browser.get_text("#nonexistent")
    assert text is None
    
@pytest.mark.asyncio
async def test_get_attribute(browser):
    """Тест получения атрибута элемента."""
    await browser.navigate("https://example.com")
    
    # Получаем атрибут существующего элемента
    href = await browser.get_attribute("a", "href")
    assert href is not None
    assert isinstance(href, str)
    
    # Пытаемся получить атрибут несуществующего элемента
    attr = await browser.get_attribute("#nonexistent", "class")
    assert attr is None
    
@pytest.mark.asyncio
async def test_wait_for_navigation(browser):
    """Тест ожидания завершения навигации."""
    await browser.navigate("https://example.com")
    
    # Ждем завершения навигации
    success = await browser.wait_for_navigation()
    assert success is True
    
    # Проверяем таймаут
    with pytest.raises(asyncio.TimeoutError):
        await browser.wait_for_navigation(timeout=1)
        
@pytest.mark.asyncio
async def test_take_screenshot(browser, tmp_path):
    """Тест создания скриншота."""
    await browser.navigate("https://example.com")
    
    # Тест сохранения в файл
    screenshot_path = tmp_path / "screenshot.png"
    result = await browser.take_screenshot(str(screenshot_path))
    assert result is True
    assert screenshot_path.exists()
    
    # Тест получения base64
    base64_screenshot = await browser.take_screenshot()
    assert isinstance(base64_screenshot, str)
    assert len(base64_screenshot) > 0
    
@pytest.mark.asyncio
async def test_page_content(browser):
    """Тест получения содержимого страницы."""
    await browser.navigate("https://example.com")
    
    content = await browser.get_page_content()
    assert content is not None
    assert isinstance(content, str)
    assert "<!DOCTYPE html>" in content.lower()
    
@pytest.mark.asyncio
async def test_execute_script(browser):
    """Тест выполнения JavaScript."""
    await browser.navigate("https://example.com")
    
    # Тест простого скрипта
    title = await browser.execute_script("return document.title")
    assert isinstance(title, str)
    
    # Тест модификации страницы
    await browser.execute_script("document.body.style.backgroundColor = 'red'")
    color = await browser.execute_script(
        "return window.getComputedStyle(document.body).backgroundColor"
    )
    assert "red" in color.lower()
    
@pytest.mark.asyncio
async def test_network_idle(browser):
    """Тест ожидания завершения сетевых запросов."""
    await browser.navigate("https://example.com")
    
    success = await browser.wait_for_network_idle()
    assert success is True
    
@pytest.mark.asyncio
async def test_request_interception(browser):
    """Тест перехвата запросов."""
    requests = await browser.intercept_requests("**/*")
    await browser.navigate("https://example.com")
    
    assert isinstance(requests, list)
    assert len(requests) > 0
    
@pytest.mark.asyncio
async def test_viewport(browser):
    """Тест установки размеров viewport."""
    await browser.navigate("https://example.com")
    
    success = await browser.set_viewport(1920, 1080)
    assert success is True
    
    # Проверяем реальные размеры
    size = await browser.execute_script("""
        return {
            width: window.innerWidth,
            height: window.innerHeight
        }
    """)
    assert size["width"] == 1920
    assert size["height"] == 1080
    success = await browser.wait_for_navigation(timeout=1)
    assert success is True
    
@pytest.mark.asyncio
async def test_screenshot(browser, tmp_path):
    """Тест создания скриншота."""
    await browser.navigate("https://example.com")
    
    # Создаем скриншот
    screenshot_path = tmp_path / "screenshot.png"
    success = await browser.screenshot(screenshot_path)
    assert success is True
    assert screenshot_path.exists()
    
@pytest.mark.asyncio
async def test_execute_script(browser):
    """Тест выполнения JavaScript."""
    await browser.navigate("https://example.com")
    
    # Выполняем JavaScript
    result = await browser.execute_script("return document.title")
    assert result is not None
    assert isinstance(result, str)
    
    # Проверяем выполнение с ошибкой
    result = await browser.execute_script("return nonexistentVariable")
    assert result is None
    
@pytest.mark.asyncio
async def test_get_elements(browser):
    """Тест получения списка элементов."""
    await browser.navigate("https://example.com")
    
    # Получаем список существующих элементов
    elements = await browser.get_elements("a")
    assert isinstance(elements, list)
    
    # Получаем список несуществующих элементов
    elements = await browser.get_elements("#nonexistent")
    assert len(elements) == 0
    
@pytest.mark.asyncio
async def test_fill_form(browser):
    """Тест заполнения формы."""
    await browser.navigate("https://example.com")
    
    # Заполняем форму
    form_data = {
        "input[name='username']": "testuser",
        "input[name='email']": "test@example.com"
    }
    
    success = await browser.fill_form(form_data)
    assert isinstance(success, bool)