import re
import time

import requests
import selenium
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


class Browser:
    def __init__(self, user, password):
        self.browser = webdriver.Chrome()
        self.user = user
        self.password = password
        self.exercises = None

    def login(self):
        self.browser.get('http://wljy.whut.edu.cn')
        self.browser.find_element_by_xpath('//a[@id="to-login-page" and text()="登录"]').click()
        self.browser.find_element_by_id('yonghuming').send_keys(self.user)
        self.browser.find_element_by_id('mima').send_keys(self.password)
        time.sleep(1)
        self.browser.find_element_by_id('loginBtn').click()
        time.sleep(5)

    def enter_curriculum(self):
        self.browser.find_element_by_id('curriculum').click()
        time.sleep(3)
        self.exercises = self.browser.find_elements_by_id('exercise')

    def practise(self):
        for exercise in self.exercises:
            try:
                time.sleep(1)
                exercise.click()
                time.sleep(1)
                self.browser.switch_to.frame(0)
                self.task()
            except selenium.common.exceptions.NoSuchFrameException as e:
                time.sleep(1)
                msg = self.browser.find_element_by_id('dialogmodalcontent').text
                print(msg)
                self.browser.find_element_by_xpath(
                    '//span[@id="dialogmodalcontent"]/../preceding-sibling::div[1]//span[text()="×" and @aria-hidden="true"]') \
                    .click()
                time.sleep(0.5)
                continue
            except Exception as e:
                print('遇到错误msg:{msg}'.format(msg=e.args[0]))
                self.browser.quit()

    def task(self):
        practices = self.browser.find_elements_by_xpath('//a[contains(@onclick,"startExercisePaper")]')
        for practice in practices:
            practice.click()
            time.sleep(2)
            windows = self.browser.window_handles
            self.browser.switch_to.window(windows[1])
            time.sleep(0.5)
            inst_no = re.findall(r"var instNo = '(\d+)';", self.browser.page_source)[-1]
            papers = self.get_paper(inst_no)
            question = self.browser.find_elements_by_xpath('//div[contains(@id,"Q_")]')

            for paper in papers:
                if paper['titleName'] in ['单选', '判断']:
                    for q in paper['questionList']:
                        answer = q['queNo'] + q['correctAnswer']
                        action = ActionChains(self.browser)
                        select = self.browser.find_element_by_xpath(
                            '//input[@id="{answer}"]'.format(answer=answer))
                        action.move_to_element(select)
                        action.click().perform()
                        time.sleep(0.5)

                if paper['titleName'] == '填空':
                    for q in paper['questionList']:
                        que_no = q['queNo']
                        self.browser.find_element_by_xpath(
                            '//textarea[@id="{que_no}"]'.format(que_no=que_no)) \
                            .send_keys(q['correctAnswer'])
                        time.sleep(0.5)
            time.sleep(2)
            self.browser.find_element_by_id('submit-paper').click()
            time.sleep(2)
            self.browser.find_element_by_id('btn-sure').click()
            time.sleep(2)
            self.browser.switch_to.window(windows[0])
            self.browser.switch_to.frame(0)
        time.sleep(1)
        self.browser.switch_to.default_content()
        action = ActionChains(self.browser)
        close = self.browser.find_element_by_xpath('//a[last()]')
        action.move_to_element(close)
        action.click().perform()

    def close(self):
        self.browser.execute_script('alert("帮你完成了所有作业，求打赏！！！")')
        time.sleep(10)
        self.browser.quit()

    @staticmethod
    def get_paper(inst_no):
        url = 'http://wljy.whut.edu.cn//exam/paperInstance/showExerciseQuestions.ajax'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
            'Referer': 'http://wljy.whut.edu.cn/web/exercise.htm?stuId=0&instNo={inst_no}&limitTime=100'.format(
                inst_no=inst_no),
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        }
        data = {
            'userid': '0',
            'instNo': inst_no
        }
        res = requests.post(url=url, headers=headers, data=data)
        if res.status_code == 200:
            res = res.json()
            if res.get('flag') == 1:
                return res['paperDetail']


if __name__ == '__main__':
    user = input('输入账号：')
    password = input('输入密码：')
    print('正在做题...')
    whlg = Browser(user=user, password=password)
    whlg.login()
    whlg.enter_curriculum()
    whlg.practise()
    whlg.close()
