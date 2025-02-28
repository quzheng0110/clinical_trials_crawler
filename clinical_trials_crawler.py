from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import random

class ClinicalTrialsCrawler:
    def __init__(self):
        self.base_url = "http://www.chinadrugtrials.org.cn"
        self.search_url = f"{self.base_url}/clinicaltrials.searchlistdetail.dhtml"
        self.data = []
        self.setup_driver()

    # 安全退出浏览器
    def safe_quit(self):
        try:
            self.driver.quit()
        except Exception as e:
            print(f"安全退出浏览器时发生错误: {e}")
        
    def setup_driver(self):
        """设置Chrome浏览器"""
        print("正在初始化浏览器...")
        options = uc.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        self.driver = uc.Chrome(options=options)
        self.driver.maximize_window()
        
    def wait_for_element(self, by, value, timeout=10):
        """等待元素出现"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"等待元素超时: {value}")
            return None

    def wait_for_elements(self, by, value, timeout=10):
        """等待多个元素出现"""
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
            return elements
        except TimeoutException:
            print(f"等待元素超时: {value}")
            return []

    def parse_table_row(self, row):
        """解析表格行数据"""
        try:
            #判断主要研究者姓名是否存在，如果存在则返回数据，否则返回None
            researcherNameElements = self.driver.find_elements(By.XPATH, "//*[@id=\"collapseTwo\"]/div/table[7]/tbody/tr[1]/td[1]")
            if len(researcherNameElements) > 0:
                return {
                    "登记号": self.driver.find_element(By.XPATH, "//*[@id=\"collapseOne\"]/div/table/tbody/tr[1]/td[1]").text.strip(),
                    "机构名称": self.driver.find_element(By.XPATH, "//*[@id=\"collapseTwo\"]/div/table[7]/tbody/tr[3]/td[2]").text.strip(),
                    "试验专业题目": self.driver.find_element(By.XPATH, "//*[@id=\"collapseTwo\"]/div/table[1]/tbody/tr[7]/td").text.strip(),
                    "适应症": self.driver.find_element(By.XPATH, "//*[@id=\"collapseTwo\"]/div/table[1]/tbody/tr[6]/td").text.strip(),
                    "药物名称": self.driver.find_element(By.XPATH, "//*[@id=\"collapseTwo\"]/div/table[1]/tbody/tr[3]/td").text.strip(),
                    "申请人名称": self.driver.find_element(By.XPATH, "//*[@id=\"collapseOne\"]/div/table/tbody/tr[3]/td").text.strip(),
                    "试验分期": self.driver.find_element(By.XPATH, "//*[@id=\"collapseTwo\"]/div/table[3]/tbody/tr[1]/td[2]").text.strip(),
                    "试验状态": self.driver.find_element(By.XPATH, "//*[@id=\"collapseOne\"]/div/table/tbody/tr[1]/td[2]").text.strip(),
                    "主要研究者姓名": self.driver.find_element(By.XPATH, "//*[@id=\"collapseTwo\"]/div/table[7]/tbody/tr[1]/td[1]").text.strip(),
                    "主要研究者单位": self.driver.find_element(By.XPATH, "//*[@id=\"collapseTwo\"]/div/table[7]/tbody/tr[3]/td[2]").text.strip()
                }
            else:
                print(f"当前项目登记号 {self.driver.find_element(By.XPATH, "//*[@id=\"collapseOne\"]/div/table/tbody/tr[1]/td[1]").text.strip()}，无法解析主要研究者姓名，跳过")
        except Exception as e:
            print(f"解析行数据时出错: {e}")
        return None

    def crawl(self, start_page=1, max_pages=28600):
        try:
            print("访问搜索页面...")
            self.driver.get(self.search_url)
            time.sleep(3)  # 等待页面完全加载
            
            # 等待并点击查询按钮
            search_button = self.wait_for_element(By.XPATH, "//input[@value='查询']")
            if search_button:
                self.driver.execute_script("arguments[0].click();", search_button)
                time.sleep(2)  # 等待查询结果加载
            

            #等待30秒，手动设置页码，可以继续从上一次中断的位置继续爬取，打开界面F12定位到下一个试验按钮，修改gotopage(1213);
            print("等待30秒，手动设置页码，可以继续从上一次中断的位置继续爬取，打开界面F12定位到下一个试验按钮，修改gotopage(1213);")
            time.sleep(30)

            current_page = start_page
            while current_page <= max_pages:
                try:
                    print(f"正在爬取第 {current_page} 页...")
                    
                    # 等待公示的试验信息显示按钮  //*[@id="headingTwo"]/h4/a
                    headingTwoBtn = self.wait_for_element(By.XPATH, "//*[@id=\"headingTwo\"]/h4/a")
                    if not headingTwoBtn:
                        print("未找到公示的试验信息显示按钮，尝试刷新页面...")
                        self.driver.refresh()
                        time.sleep(5)
                        continue
                    
                    # 点击公示的试验信息按钮
                    self.driver.execute_script("arguments[0].click();", headingTwoBtn)
                    time.sleep(1)
                    
                    # 解析当前页数据
                    registerNo = self.wait_for_elements(By.XPATH, "//*[@id=\"collapseTwo\"]/div/table[1]/tbody/tr[1]/td")
                    if not registerNo:
                        print("未找到数据行，可能已到达最后一页")
                        break

                    print(registerNo)
                    
                    page_data = []
                    for row in registerNo:
                        data = self.parse_table_row(row)
                        print(f"解析出来数据为： {data}")
                        if data:
                            page_data.append(data)
                    
                    if page_data:
                        self.data.extend(page_data)
                        print(f"第 {current_page} 页成功爬取 {len(page_data)} 条数据")
                    else:
                        print(f"第 {current_page} 页未找到有效数据，可能已到达最后一页")
                        break
                    
                    # 点击下一页
                    try:
                        # 找到下一个试验按钮
                        # 获取所有导航按钮
                        nav_buttons = self.driver.find_elements(By.XPATH, "//*[@id=\"toolbar_top\"]/div/a")
                        
                        if len(nav_buttons) == 0:
                            print("未找到任何导航按钮，可能已到达最后一页")
                            break
                        elif len(nav_buttons) == 1:
                            # 第一页只有"下一个试验"按钮
                            if "下一个试验" in nav_buttons[0].text:
                                self.driver.execute_script("arguments[0].click();", nav_buttons[0])
                            else:
                                # 最后一页只有"上一个试验"按钮
                                print("已到达最后一页")
                                break
                        elif len(nav_buttons) == 2:
                            # 中间页面有两个按钮，点击"下一个试验"
                            if "下一个试验" in nav_buttons[1].text:
                                self.driver.execute_script("arguments[0].click();", nav_buttons[1])
                            else:
                                print("未找到下一页按钮，可能已到达最后一页")
                                break
                        
                        current_page += 1
                        # 等待新页面加载
                        time.sleep(1)
                    except NoSuchElementException:
                        print("未找到下一页按钮，可能已到达最后一页")
                        break
                    
                    # 随机延迟
                    delay = random.uniform(2, 4)
                    print(f"等待 {delay:.1f} 秒后继续...")
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"处理页面时出错: {e}")
                    print("尝试重新加载页面...")
                    self.driver.refresh()
                    time.sleep(5)
                    continue
                    
        except Exception as e:
            print(f"爬取过程出错: {e}")
        finally:
            self.driver.quit()
    
    def save_to_excel(self, filename="clinical_trials_data.xlsx"):
        if not self.data:
            print("没有数据可供保存")
            return
            
        try:
            print(f"正在将{len(self.data)}条数据保存到Excel文件...")
            df = pd.DataFrame(self.data)
            
            try:
                # 尝试使用openpyxl引擎保存Excel
                df.to_excel(filename, index=False, engine='openpyxl')
                print(f"数据已成功保存到Excel(openpyxl)文件: {filename}")
            except ImportError as e:
                print(f"保存Excel文件失败 (openpyxl错误): {e}")
                print("尝试使用其他Excel引擎...")
                try:
                    # 尝试使用xlsxwriter引擎
                    df.to_excel(filename, index=False, engine='xlsxwriter')
                    print(f"数据已成功保存到Excel(xlsxwriter)文件: {filename}")
                except ImportError:
                    # 如果Excel保存都失败，则保存为CSV
                    csv_filename = filename.replace('.xlsx', '.csv')
                    print(f"Excel保存失败，正在保存为CSV文件: {csv_filename}")
                    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                    print(f"数据已成功保存到CSV文件: {csv_filename}")
            
            print(f"共保存 {len(self.data)} 条数据")
        except Exception as e:
            print(f"保存数据时发生错误: {str(e)}")
            # 确保在发生任何错误时都尝试保存为CSV
            try:
                csv_filename = filename.replace('.xlsx', '.csv')
                print(f"尝试保存为CSV文件: {csv_filename}")
                df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                print(f"数据已成功保存到CSV文件: {csv_filename}")
            except Exception as csv_error:
                print(f"保存CSV文件也失败了: {str(csv_error)}")

def main():
    crawler = ClinicalTrialsCrawler()
    # 可以根据需要调整页数
    maxCount = 28600
    crawler.crawl(start_page=1213, max_pages=maxCount) 
    # 获取当前时间
    current_time = datetime.now()
    # 格式化为指定格式：yyyymmddHHmmss
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")
    # 构建文件名
    filename = f"clinical_trials_data_{formatted_time}_{maxCount}.xlsx"
    crawler.save_to_excel(filename=filename)
    print("爬取完成")
    crawler.safe_quit()

if __name__ == "__main__":
    main() 
