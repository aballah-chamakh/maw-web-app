class input_has_no_empty_value(object):

  def __init__(self, locator):
    self.locator = locator


  def __call__(self, driver):
    element = driver.find_element(*self.locator)   # Finding the referenced element
    if element.get_attribute("value") :
        return element
    else:
        return False
