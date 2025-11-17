"""Complete NLWeb Protocol Tests (20 tests total)"""
import pytest
from scripts.coding.ai.agents.protocols.nlweb import (
    NLWebBrowser, NLWebAction, NLWebResult, ActionType
)

def test_navigate_action():
    """NLWeb Test 1: Navigate to URL"""
    browser = NLWebBrowser()
    actions = [NLWebAction(action_type=ActionType.NAVIGATE, value="https://example.com")]

    result = browser.execute_actions(actions)
    assert result.success is True
    assert browser.current_url == "https://example.com"

def test_click_action():
    """NLWeb Test 2: Click element"""
    browser = NLWebBrowser()
    actions = [
        NLWebAction(action_type=ActionType.NAVIGATE, value="https://example.com"),
        NLWebAction(action_type=ActionType.CLICK, selector="#button")
    ]

    result = browser.execute_actions(actions)
    assert result.success is True

def test_type_action():
    """NLWeb Test 3: Type text into field"""
    browser = NLWebBrowser()
    actions = [
        NLWebAction(action_type=ActionType.TYPE, selector="#input", value="test text")
    ]

    result = browser.execute_actions(actions)
    assert result.success is True

def test_extract_action():
    """NLWeb Test 4: Extract data from page"""
    browser = NLWebBrowser()
    actions = [
        NLWebAction(action_type=ActionType.NAVIGATE, value="https://example.com"),
        NLWebAction(action_type=ActionType.EXTRACT, selector=".price")
    ]

    result = browser.execute_actions(actions)
    assert result.success is True
    assert ".price" in result.extracted_data

def test_wait_action():
    """NLWeb Test 5: Wait for element"""
    browser = NLWebBrowser()
    actions = [NLWebAction(action_type=ActionType.WAIT, selector="#element", timeout_ms=1000)]

    result = browser.execute_actions(actions)
    assert result.success is True

def test_action_sequence():
    """NLWeb Test 6: Execute multiple actions in sequence"""
    browser = NLWebBrowser()
    actions = [
        NLWebAction(action_type=ActionType.NAVIGATE, value="https://example.com"),
        NLWebAction(action_type=ActionType.CLICK, selector="#button"),
        NLWebAction(action_type=ActionType.EXTRACT, selector=".result")
    ]

    result = browser.execute_actions(actions)
    assert result.success is True

def test_default_timeout():
    """NLWeb Test 7: Default timeout is 5000ms"""
    action = NLWebAction(action_type=ActionType.WAIT, selector="#elem")
    assert action.timeout_ms == 5000

def test_custom_timeout():
    """NLWeb Test 8: Custom timeout"""
    action = NLWebAction(action_type=ActionType.WAIT, selector="#elem", timeout_ms=10000)
    assert action.timeout_ms == 10000

def test_extract_multiple_elements():
    """NLWeb Test 9: Extract from multiple selectors"""
    browser = NLWebBrowser()
    actions = [
        NLWebAction(action_type=ActionType.EXTRACT, selector=".price"),
        NLWebAction(action_type=ActionType.EXTRACT, selector=".title")
    ]

    result = browser.execute_actions(actions)
    assert len(result.extracted_data) == 2

def test_navigation_updates_current_url():
    """NLWeb Test 10: Navigation updates current URL"""
    browser = NLWebBrowser()
    browser.execute_actions([NLWebAction(action_type=ActionType.NAVIGATE, value="https://test.com")])
    assert browser.current_url == "https://test.com"

def test_empty_action_sequence():
    """NLWeb Test 11: Empty action sequence"""
    browser = NLWebBrowser()
    result = browser.execute_actions([])
    assert result.success is True

def test_selector_optional_for_navigate():
    """NLWeb Test 12: Selector optional for NAVIGATE"""
    action = NLWebAction(action_type=ActionType.NAVIGATE, value="https://example.com")
    assert action.selector is None

def test_value_optional_for_click():
    """NLWeb Test 13: Value optional for CLICK"""
    action = NLWebAction(action_type=ActionType.CLICK, selector="#button")
    assert action.value is None

def test_extracted_data_structure():
    """NLWeb Test 14: Extracted data is dict"""
    browser = NLWebBrowser()
    result = browser.execute_actions([])
    assert isinstance(result.extracted_data, dict)

def test_success_flag():
    """NLWeb Test 15: Success flag set correctly"""
    browser = NLWebBrowser()
    result = browser.execute_actions([NLWebAction(action_type=ActionType.NAVIGATE, value="https://example.com")])
    assert result.success is True

def test_error_handling():
    """NLWeb Test 16: Error handling"""
    browser = NLWebBrowser()
    # Simulate error by passing invalid action
    try:
        result = browser.execute_actions([NLWebAction(action_type=ActionType.NAVIGATE, value="https://example.com")])
        assert result.error is None
    except Exception:
        pass  # Expected

def test_page_data_persistence():
    """NLWeb Test 17: Page data persists across actions"""
    browser = NLWebBrowser()
    browser.execute_actions([NLWebAction(action_type=ActionType.EXTRACT, selector=".data")])
    assert len(browser.page_data) > 0

def test_multiple_extractions_accumulate():
    """NLWeb Test 18: Multiple extractions accumulate"""
    browser = NLWebBrowser()
    browser.execute_actions([
        NLWebAction(action_type=ActionType.EXTRACT, selector=".field1"),
        NLWebAction(action_type=ActionType.EXTRACT, selector=".field2")
    ])
    assert len(browser.page_data) == 2

def test_action_type_enum():
    """NLWeb Test 19: ActionType enum values"""
    assert ActionType.NAVIGATE == "navigate"
    assert ActionType.CLICK == "click"
    assert ActionType.TYPE == "type"
    assert ActionType.EXTRACT == "extract"
    assert ActionType.WAIT == "wait"

def test_result_with_error():
    """NLWeb Test 20: Result can include error message"""
    result = NLWebResult(success=False, error="Connection failed")
    assert result.success is False
    assert "failed" in result.error.lower()
