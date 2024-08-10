from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from urllib.parse import urlparse


class ProductParser:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=options)

        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

    def find_product_name_by_meta(self):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, "meta[itemprop='name']").get_attribute("content")
        except:
            return None

    def find_product_name_by_h1(self):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, "h1[itemprop='name']").text
        except:
            return None

    def find_product_name_by_url(self, url):
        try:
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.split("/")
            product_name = "/".join(path_parts[-2:])
            product_name = product_name.replace('.html', '')
            return product_name
        except:
            return None

    def find_product_price_by_meta(self):
        try:
            price_element = self.driver.find_element(By.CSS_SELECTOR, "meta[itemprop='price']").get_attribute("content")
            if price_element:
                return price_element
        except:
            pass

        try:
            price_element = self.driver.find_element(By.CSS_SELECTOR, "[itemprop='price']").text
            if price_element:
                return price_element
        except:
            pass

        return None

    def find_product_price_by_class(self):
        try:
            price_element = self.driver.find_element(By.CSS_SELECTOR, "[class*=price]")
            if price_element:
                return price_element.text
            else:
                return None
        except:
            return None

    def check_availability(self, button_texts):
        availability = 'Не доступен к заказу'
        for button_text in button_texts:
            try:
                button = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{button_text}')]")
                if button:
                    availability = 'Доступен к заказу'
                break
            except:
                continue
        return availability

    def find_description(self):
        try:
            description_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'description')]")
            if description_elements:
                return "\n".join([element.text.strip() for element in description_elements])
        except:
            pass
        try:
            description_element = self.driver.find_element(By.CSS_SELECTOR, "[itemprop='description']").get_attribute("content")
            if description_element:
                return description_element
        except:
            pass
        try:
            dl_elements = self.driver.find_elements(By.TAG_NAME, "dl")
            if dl_elements:
                return "\n".join([element.text.strip() for element in dl_elements])
        except:
            pass
        try:
            li_elements = self.driver.find_elements(By.TAG_NAME, "li")
            if li_elements:
                return "\n".join([element.text.strip() for element in li_elements])
        except:
            pass

        return "Нет описания"

    def find_max_resolution_image(self):
        max_resolution = 0
        max_resolution_image_src = ""
        images = self.driver.find_elements(By.TAG_NAME, "img")
        for image in images:
            src = image.get_attribute("src")
            if src:
                resolution = image.size['width'] * image.size['height']
                if resolution > max_resolution:
                    max_resolution = resolution
                    max_resolution_image_src = src
        return max_resolution_image_src if max_resolution_image_src else 'Нет изображения'

    def parse_product(self, url):
        self.driver.get(url)

        product_name = self.find_product_name_by_meta()
        if not product_name:
            product_name = self.find_product_name_by_h1()
        if not product_name:
            product_name = self.find_product_name_by_url(url)

        product_price = self.find_product_price_by_meta()
        if not product_price:
            product_price = self.find_product_price_by_class()
        if not product_price:
            product_price = "Нет данных"

        product_description = self.find_description()
        button_texts = ["Купить", "В корзину", "Купить в 1 клик", "Купить в один клик"]
        availability = self.check_availability(button_texts)

        image_link = self.find_max_resolution_image()

        return {
            'Название': product_name,
            'Цена': product_price,
            'Доступность заказа': availability,
            'Ссылка на изображение': image_link,
            'Ссылка на товар': url,
            'Характеристики': product_description
        }

    def quit_driver(self):
        self.driver.quit()