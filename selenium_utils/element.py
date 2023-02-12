import logging
import time

from selenium.common import exceptions
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common import action_chains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium_utils import exception

logger = logging.getLogger(__name__)

def find_elements_multiple(driver: WebDriver, locators: list[tuple]):
    """Return a list of WebElements found on a page from a list of locators.
    Args:
        driver (WebDriver)
        locators (list[tuple]): Locators in format (identifier, locator)
    Returns:
        list[selenium.webdriver.remote.webelement.WebElement]
    """
    return [element for locator in locators for element in driver.find_elements(*locator)]



def hover_over_element(driver: WebDriver, element):
    """Moves the mouse pointer to the element and hovers"""
    action_chains.ActionChains(driver).move_to_element(element).perform()


def wait_until_stops_moving(element, wait_seconds=1):
    """Waits until the element stops moving
    Args:
        selenium.webdriver.remote.webelement.WebElement
    """

    prev_location = None
    timer_begin = time.time()

    while prev_location != element.location:
        prev_location = element.location
        time.sleep(0.1)

        if time.time() - timer_begin > wait_seconds:
            raise exception.ElementMovingTimeout


def get_when_visible(driver: WebDriver, locator, wait_seconds=1):
    """
    Args:
      driver (base.CustomDriver)
      locator (tuple)
    Returns:
        selenium.webdriver.remote.webelement.WebElement
    """
    return WebDriverWait(
        driver,
        wait_seconds) \
        .until(EC.presence_of_element_located(locator))


def wait_until_condition(driver: WebDriver, condition, wait_seconds=1):
    """Wait until given expected condition is met"""
    WebDriverWait(
        driver,
        wait_seconds).until(condition)


def wait_until_not_present(driver: WebDriver, locator):
    """Wait until no element(-s) for locator given are present in the DOM."""
    wait_until_condition(driver, lambda d: len(d.find_elements(*locator)) == 0)


def get_when_all_visible(driver: WebDriver, locator, wait_seconds=1):
    """Return WebElements by locator when all of them are visible.
    Args:

      locator (tuple)
    Returns:
        selenium.webdriver.remote.webelement.WebElements
    """
    return WebDriverWait(
        driver,
        wait_seconds) \
        .until(EC.visibility_of_any_elements_located(locator))


def get_unique_element_from_possible_elements(driver: WebDriver, list_of_locators:list[tuple], ec=EC.visibility_of_element_located, wait_seconds=1,  webDriverWait=WebDriverWait):
    """Return a unique WebElement found on a page from a list of (possible) elements, when meeting an (allowable) 'expected condition' (dafaults to: `EC.visibility_of_element_located`).
    Raises an exception if none or more than 1 elements match criteria.

    Args:
        driver (WebDriver)
        list_of_locators (list[tuple]): Locators in format (identifier, locator) of WebElements that may or may not satisfy the supplied `Expected Condition`
        ec (function): Expected Condition by which to seek WebElements [EC.visibility_of_element_located, EC.invisibility_of_element_located, EC.presence_of_element_located]
        wait_seconds (int):
    Returns:
        selenium.webdriver.remote.webelement.WebElement
    Raises 
        exception.MultipleElementsFound - if more than one element is found.
        exception.NoSuchElementException - if no element is found.

    Notes: 
        Need read more about how find_element() works, and how whether it will return for all the `Expected Conditions` we cater.
    """
    if ec not in [EC.visibility_of_element_located, EC.invisibility_of_element_located, EC.presence_of_element_located]:
        raise exception.InvalidExpectedCondition(f"Invalid `Expected Condition` ({ec}). Please choose from: `EC.visibility_of_element_located`, `EC.invisibility_of_element_located`, `EC.presence_of_element_located`")
    
    list_of_ecs = [ec(el) for el in list_of_locators]  # create a list of expected conditions from the list of locators
    try:
        webDriverWait(driver, timeout=wait_seconds).until(EC.any_of(*list_of_ecs))  # wait for any of the expected conditions to be met
    except exceptions.TimeoutException:
        raise exception.NoExpectedConditionsMet(f"No `Expected Conditions` were met.")

    list_matched_locators = []
    for locator in list_of_locators:
        try:
            list_matched_locators.append(driver.find_element(*locator))
        except exceptions.NoSuchElementException:
            pass  # no element was found for this locator/expected condition

    if len(list_matched_locators) == 1:  # One or more elements were found for this locator. NB: Nuance is that this is the first element found, not necessarily the only element found.
        return list_matched_locators[0]
    elif len(list_matched_locators) == 0:  # No elements were found for this locator
        raise exception.NoExpectedConditionsMet(f"No `Expected Conditions` were met.")
    else:
        raise exception.MultipleExpectedConditionsMet(f"Multiple `Expected Conditions` were met ({list_matched_locators})")


def get_when_clickable(driver: WebDriver, locator, wait_seconds=1):
    """
    Args:
      driver (base.CustomDriver)
      locator (tuple)
    Returns:
        selenium.webdriver.remote.webelement.WebElement
    """
    return WebDriverWait(
        driver,
        wait_seconds) \
        .until(EC.element_to_be_clickable(locator))


def get_when_invisible(driver: WebDriver, locator, wait_seconds=1):
    """
    Args:
      driver (base.CustomDriver)
      locator (tuple)
    Returns:
        selenium.webdriver.remote.webelement.WebElement
    """
    return WebDriverWait(
        driver,
        wait_seconds) \
        .until(EC.invisibility_of_element_located(locator))


def wait_for_element_text(driver: WebDriver, locator, text, wait_seconds=1):
    """
      Args:
        driver (base.CustomDriver)
        locator (tuple)
        text (str)
    """
    return WebDriverWait(
        driver,
        wait_seconds) \
        .until(EC.text_to_be_present_in_element(locator, text))


def is_value_in_attr(element, attr="class", value="active"):
    """Checks if the attribute value is present for given attribute
    Args:
      element (selenium.webdriver.remote.webelement.WebElement)
      attr (basestring): attribute name e.g. "class"
      value (basestring): value in the class attribute that
        indicates the element is now active/opened
    Returns:
        bool
    """
    attributes = element.get_attribute(attr)
    return value in attributes.split()


def click_on_staleable_element(driver: WebDriver, el_locator, wait_seconds=1):
    """Clicks an element that can be modified between the time we find it and when we click on it"""
    time_start = time.time()

    while time.time() - time_start < wait_seconds:
        try:
            driver.find_element(*el_locator).click()
            break
        except exceptions.StaleElementReferenceException as e:
            logger.error(str(e))
            time.sleep(0.1)
    else:
        raise exception.ElementNotFound(el_locator)


def scroll_into_view(driver: WebDriver, element, offset_pixels=0):
    """Scrolls page to element using JS"""
    driver.execute_script("return arguments[0].scrollIntoView();", element)

    # compensate for the header
    driver.execute_script("window.scrollBy(0, -{});".format(offset_pixels))
    return element
