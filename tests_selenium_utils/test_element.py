from selenium_utils.element import *
from selenium_utils.exception import *

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

import pytest

import logging
log = logging.getLogger(__name__)

import pytest
from unittest.mock import Mock
from selenium import webdriver

@pytest.fixture
def mock_webdriver():
    mock_webdriver = Mock(spec=webdriver.Firefox)
    yield mock_webdriver

@pytest.fixture
def mock_webDriverWait(mock_webdriver):
    mock_webDriverWait = Mock(spec=webdriver.support.ui.WebDriverWait)
    return mock_webDriverWait

@pytest.fixture
def mock_WebElement():
    mock_WebElement = Mock(spec=webdriver.remote.webelement.WebElement)
    return mock_WebElement  

@pytest.fixture
def list_of_locators():
    return [(By.XPATH, "//element1"), (By.XPATH, "//element2")]

# Dont know how to test this one
def test_get_unique_element_from_list_possible_elements_with_one_matching_element(mock_webdriver, mock_WebElement, list_of_locators):
    pass
    # assert isinstance(result, WebElement)


def test_get_unique_element_from_list_possible_elements_with_no_matching_element(mock_webdriver, list_of_locators):
    mock_webdriver.find_element.side_effect = exceptions.NoSuchElementException
    with pytest.raises(exception.NoExpectedConditionsMet):
        get_unique_element_from_possible_elements(mock_webdriver, list_of_locators)


def test_get_unique_element_from_list_possible_elements_with_multiple_matching_elements(mock_webdriver, mock_WebElement, list_of_locators):
    mock_WebElement.is_displayed.return_value = True
    mock_webdriver.find_element.return_value = mock_WebElement
    with pytest.raises(exception.MultipleExpectedConditionsMet):
        get_unique_element_from_possible_elements(mock_webdriver, list_of_locators*2)


def test_get_unique_element_from_list_possible_elements_with_invalid_expected_condition(mock_webdriver, list_of_locators):  
    ec = lambda x: x
    with pytest.raises(exception.InvalidExpectedCondition):
        get_unique_element_from_possible_elements(mock_webdriver, list_of_locators, ec=ec)


def test_find_elements_multiple(mock_webdriver, mock_WebElement):
    locators = [('id', 'element_id'), ('class name', 'element_class')]
    mock_webdriver.find_elements.return_value = [mock_WebElement, mock_WebElement]  # mock result simulate getting two elements for each of the locators
    result = find_elements_multiple(mock_webdriver, locators)
    log.debug(f"result: {result}")
    assert isinstance(result, list)
    assert all(isinstance(element, WebElement) for element in result)

def test_find_elements_multiple_empty_list(mock_webdriver):
    locators = []
    result = find_elements_multiple(mock_webdriver, locators)
    assert result == []