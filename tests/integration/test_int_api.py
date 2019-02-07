#
# import requests
#
#
# def test_1(image):
#     # client.images.build(path=base, tag=image_name, rm=False)
#
#     # TODO: remove me
#     print(111, 'test_int_api.py:6', image)
# #
# def test_run(image, image_name, client):
#     c = client.containers.run(image_name,
#                               ports={8000: 9999},
#                               remove=True,
#                               detach=True)
#     c.stop()
#
#
# def test_client(container):
#     res = requests.get('http://localhost:13141/+api')
#     c = res.json()
#     assert c['result']['login'] == 'http://localhost:13141/+login'
#
# from selenium import webdriver
# driver = webdriver.PhantomJS()
# driver.set_window_size(1120, 550)
# driver.get("https://duckduckgo.com/")
# driver.find_element_by_id('search_form_input_homepage').send_keys("realpython")
# driver.find_element_by_id("search_button_homepage").click()
# print(driver.current_url)
# driver.quit()
