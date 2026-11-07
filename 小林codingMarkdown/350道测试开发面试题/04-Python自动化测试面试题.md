---
title: Python自动化测试面试题
book: 350道测试开发面试题
source: 350道测试开发面试题-小林coding-v2.0.pdf
pages: 59-97
---

# Python自动化测试面试题

测试开发训练营：针对面试求职的测试开发训练营，大厂导师 1v1 私教，帮助学员从 0 到 1 拿到测开满意的 offer

直播授课+实时互动答疑，课程到就业贯穿企业级案例，由测试开发导师全程主讲，绝无其他助理老师代课。

- 大厂测试开发导师一对一求职陪跑，覆盖课程答疑+简历打磨+面试模拟面试+面试复盘等求职辅导

## 一、接又自动化(高优)

_1._ 你在项目中使用的接又自动化测试框架是什么？为什么选择它？

**回答话术：**

我使用的是 **Requests + Pytest + Allure** 组合框架。选择它主要基于三个原因：

首先，Requests库非常简洁易用，支持所有HTTP方法，能自动处理Session和Cookie，满足大部分接又测试需求。

其次，Pytest提供了强大的fixture机制和参数化功能，可以很好地管理测试数据和前置后置条件，而且失败重跑、 并发执行这些功能都有现成的插件支持，非常适合做CI/CD集成。

最后，Allure能生成非常直观的HTML测试报告，支持用例分类、历史趋势分析，方便向团队展示测试结果。

这套组合既满足了功能测试需求，学习成本也不高，团队成员上手很快。

### _2._ 请描述你设计的接又自动化测试框架的整体架构

**回答话术：**

我设计的框架采用分层架构，主要分为五层：

**第一层是API层**，负责封装所有接又请求，按业务模块划分文件，比如user_api.py、order_api.py，每个接又对应一个方法。

**第二层是测试用例层**，这里只关注测试逻辑，调用API层的方法，不涉及具体的请求细节。

**第三层是公共工具层**，封装了请求发送、日志记录、断言验证等通用功能，避免重复代码。

**第四层是配置层**，使用YAML文件管理不同环境的配置，支持开发、测试、生产环境快速切换。

**第五层是数据层**，测试数据独立管理，支持YAML、JSON、Excel等多种格式。

这样设计的好处是职责清晰、易于维护，修改接又只需要改API层，修改测试数据不影响用例代码。

### _3._ 如何实现接又请求的二次封装？

**回答话术：**

我会创建一个RequestUtil工具类，对Requests库进行二次封装。主要实现四个功能： **第一是统一请求入又**，封装get、post、put、delete等方法，所有请求都走这个工具类。 **第二是自动记录日志**，在发送请求前后自动打印请求URL、参数、响应结果，方便定位问题。 **第三是统一异常处理**，捕获超时、连接异常等错误，统一处理并记录。

**第四是Session管理**，使用Session对象自动管理Cookie，支持全局设置token。

```
class RequestUtil:
    def send_request(self, method, url, **kwargs):
        logger.info(f"请求: {method} {url}")
        response = self.session.request(method, url, **kwargs)
        logger.info(f"响应: {response.status_code}")
        return response
```

这样封装后，测试用例中只需要关注业务逻辑，不用每次都写日志和异常处理代码。

### _4._ 如何设计 _API_ 层实现接又的统一管理？

**回答话术：**

我会先创建一个BaseApi基类，里面封装公共的请求方法。然后针对每个业务模块创建独立的API类，继承 BaseApi。

比如UserApi类专门管理用户相关接又，每个接又封装成一个方法，方法名语义化，参数清晰。

```
class UserApi(BaseApi):
    def login(self, username, password):
        return self.send('POST', '/api/login',
                        json={'username': username, 'password': password})

    def get_user_info(self, user_id):
        return self.send('GET', f'/api/users/{user_id}')
```

这样设计的优点是：接又按模块分类很清晰，调用时语义明确，而且如果接又有变化，只需要修改对应的API类， 测试用例不受影响。

### _5._ 如何实现多环境配置管理？

**回答话术：**

我使用YAML文件管理配置，在config.yaml中定义dev、test、prod三个环境的配置，包括接又域名、数据库连接信息等。

然后创建Config类读取配置，支持通过环境变量或配置文件切换环境。

```
env: test
test:
  base_url: http://test-api.example.com
  db:
    host: test-db.example.com
```

切换环境有两种方式：一是修改配置文件中的env值，二是通过环境变量 `export TEST_ENV=dev` 来指定。 这样做的好处是配置集中管理，切换环境很方便，而且不用在代码里硬编码环境信息。

### _6._ 如何实现测试数据的参数化？

**回答话术：**

我主要用两种方式管理测试数据：

**第一种是使用Pytest的parametrize装饰器**，适合数据量少的场景，直接在用例上标注。

```
@pytest.mark.parametrize("username,password,expected", [
    ("admin", "123456", 0),
    ("admin", "wrong", 1001),
])
def test_login(self, username, password, expected):
    response = self.user_api.login(username, password)
    assert response.json()['code'] == expected
```

**第二种是外部数据文件**，用YAML或Excel存储测试数据，通过工具类读取后传给parametrize。适合数据量大或需要非技术人员维护数据的场景。

这样实现数据驱动测试，同一个用例可以跑多组数据，代码复用率高。

### _7._ 如何实现统一的断言机制？

**回答话术：**

我封装了一个AssertUtil工具类，提供常用的断言方法：

```
class AssertUtil:
    @staticmethod
    def assert_code(response, expected_code):
        assert response.status_code == expected_code

    @staticmethod
    def assert_json_value(response, json_path, expected_value):
        actual = jsonpath(response.json(), json_path)[0]
        assert actual == expected_value
```

主要提供四类断言：状态码断言、JSON字段值断言、响应时间断言、字段存在性断言。

每个断言方法都会自动记录日志，失败时输出详细的对比信息，方便定位问题。

这样做的好处是断言逻辑统一，输出格式一致，而且可以在断言方法里加入更多增强功能，比如失败截图、失败重试等。

### _8. Pytest_ 的 _fixture_ 在框架中如何应用？

**回答话术：**

我主要用fixture实现三类功能：

**第一是环境准备**，比如用session级别的fixture获取登录token，整个测试会话只登录一次，所有用例共享。 **第二是数据准备和清理**，用yield实现，测试前创建数据，测试后自动删除，保证环境干净。

`@pytest.fixture def create_user(self): user_id = self.user_api.create_user() yield user_id self.user_api.delete_user(user_id)  #` 自动清理

**第三是依赖注入**，fixture可以相互依赖，比如auth_headers依赖login_token，自动组装测试所需的数据。

通过不同的scope控制fixture的生命周期，function、class、module、session灵活选择。

### _9._ 如何在框架中实现日志管理？

**回答话术：**

我使用Python的logging模块实现日志管理，封装了一个Logger工具类。

主要实现四个功能：

**第一是分级输出**，设置DEBUG、INFO、ERROR等不同级别，开发时用DEBUG，正式运行用INFO。

**第二是双重输出**，日志同时输出到控制台和文件，文件按日期自动分割。

**第三是格式统一**，日志包含时间、级别、文件名、行号、具体内容，便于追溯。

```
formatter = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
```

**第四是与Allure集成**，把日志附加到测试报告中，失败时可以直接在报告里查看日志。

这样做可以快速定位问题，特别是CI/CD环境中看不到控制台输出时，日志文件非常重要。

### _10._ 如何处理接又的依赖关系？

**回答话术：**

接又依赖主要有两类：

**第一类是token依赖**，很多接又需要先登录获取token。我用fixture实现，在conftest.py中创建login_token的 fixture，需要认证的用例直接引用这个fixture。

**第二类是数据依赖**，比如测试订单详情接又需要先创建订单。我也用fixture实现，用yield保证数据用完后清理。

`@pytest.fixture def order_id(self): #` 创建订单 `response = self.order_api.create_order() order_id = response.json()['data']['id'] yield order_id #` 测试完成后删除订单 `self.order_api.delete_order(order_id)`

复杂场景下，我会在API类中封装组合接又方法，把多个有依赖关系的接又调用封装成一个方法，用例直接调用。

### _11._ 如何实现接又测试报告？

**回答话术：**

我使用Allure生成测试报告，主要包含五个步骤：

**第一步安装插件**：pytest-allure-adaptor

**第二步在用例中添加装饰器**，标注用例的功能模块、优先级、标签等。

`@allure.feature("` 用户模块 `") @allure.story("` 用户登录 `") @allure.severity("blocker") def test_login(self): pass`

**第三步在断言或关键步骤添加日志**，使用allure.attach添加截图、请求响应等附件。

**第四步执行用例时生成JSON数据**： `pytest --alluredir=./report`

**第五步生成HTML报告**： `allure generate ./report -o ./html --clean`

报告中可以看到用例执行情况、成功率、失败原因、历史趋势等，非常直观，适合向项目组展示。

### _12._ 如何实现接又的数据库校验？

**回答话术：**

我封装了一个DBUtil工具类，使用PyMySQL或SQLAlchemy连接数据库。

典型使用场景是：调用创建订单接又后，查询数据库验证订单记录是否正确插入。

```
class DBUtil:
    def query(self, sql):
        cursor.execute(sql)
        return cursor.fetchall()
```

 # 使用示例 def test_create_order(self): response = self.order_api.create_order() order_id = response.json()['data']['order_id'] # 数据库校验 sql = f"SELECT * FROM orders WHERE id={order_id}" result = self.db.query(sql) assert result[0]['status'] == 'created'

需要注意的是，数据库连接信息从配置文件读取，不同环境连接不同数据库。而且用完要及时关闭连接，避免连接泄露。

### _13._ 如何处理接又的加密和签名？

**回答话术：**

我遇到过两种常见场景：

**第一种是参数签名**，比如MD5签名。我会在BaseApi中封装generate_sign方法，按照约定的规则（参数排序、拼接、加密）生成签名，发送请求前自动添加。

```
def generate_sign(self, params):
    sorted_str = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
    return hashlib.md5((sorted_str + SECRET_KEY).encode()).hexdigest()
```

**第二种是响应解密**，比如AES加密。在RequestUtil的send_request方法中，收到响应后先判断是否加密，如果加密就先解密再返回。

我会把加解密逻辑封装成独立的工具类，这样修改加密算法时不影响其他代码。

### _14._ 如何实现接又的 _Mock_ 测试？

**回答话术：**

我主要用两种方式实现Mock：

**第一种是使用responses库**，拦截Requests请求，返回预设的响应数据，适合测试环境不稳定或依赖的第三方接又还没开发完成的情况。

```
import responses
```

```
@responses.activate
def test_with_mock(self):
    responses.add(responses.GET, 'http://api.example.com/user',
                 json={'code': 0, 'data': {'name': 'test'}}, status=200)

    response = requests.get('http://api.example.com/user')
    assert response.json()['code'] == 0
```

**第二种是搭建Mock Server**，使用mitmproxy或WireMock，可以模拟更复杂的场景，比如延迟响应、返回错误等。 Mock主要用于开发阶段和异常场景测试，不能完全替代真实接又测试。

### _15._ 如何实现失败重试机制？

**回答话术：**

我用pytest-rerunfailures插件实现失败重试，有两种使用方式：

**第一种是全局配置**，在pytest.ini中配置重试次数，所有失败用例自动重试。

```
[pytest]
reruns = 2
reruns_delay = 1
```

**第二种是针对特定用例**，用装饰器标注。

```
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_unstable_api(self):
    pass
```

重试适合网络不稳定或偶发性失败的场景，但要注意不能滥用，如果接又本身有问题，重试多少次都会失败，要先定位根本原因。

### _16._ 如何实现并发测试？

**回答话术：**

我使用pytest-xdist插件实现并发执行，通过-n参数指定并发数。

`pytest -n 4 # 4` 个进程并发执行

需要注意三点：

**第一是数据隔离**，每个用例使用独立的测试数据，避免并发时互相影响。

**第二是共享资源加锁**，如果多个用例操作同一资源（比如同一个用户），需要加文件锁或分布式锁。 **第三是fixture的scope设置**，session级别的fixture在并发时每个worker都会执行一次，要根据实际情况调整。 并发能大幅提升执行效率，但也增加了测试的复杂度，要在速度和稳定性之间权衡。

### _17._ 如何实现持续集成 _CI/CD_？

**回答话术：**

我们项目用Jenkins做持续集成，主要配置流程是：

**第一步，代码提交触发Jenkins任务**，可以是定时触发或Git提交触发。

**第二步，拉取最新代码，安装依赖**： `pip install -r requirements.txt` **第三步，执行测试用例**： `pytest testcases/ --alluredir=./report` **第四步，生成Allure报告**： `allure generate ./report`

**第五步，发送测试报告**，通过邮件或企业微信机器人推送报告链接和测试结果统计。

`#` 获取测试结果 `result = {"total": 100, "pass": 95, "fail": 5} #` 发送通知 `send_wechat_notification(result)`

关键是要保证测试环境稳定，用例执行快速，失败时能快速定位问题。

### _18._ 如何实现接又性能测试？

**回答话术：**

我主要用Locust做接又性能测试，可以复用接又自动化的API封装。

```
from locust import HttpUser, task, between
class UserBehavior(HttpUser):
    wait_time = between(1, 3)

    @task
    def test_login(self):
        self.client.post("/api/login",
                        json={"username": "test", "password": "123456"})
```

执行命令： `locust -f locustfile.py --host=http://test.example.com`

可以在Web界面设置并发用户数和增长率，实时查看TPS、响应时间、失败率等指标。

性能测试一般在功能测试通过后进行，主要关注接又的响应时间、并发能力、稳定性，发现性能瓶颈。

### _19._ 如何管理和维护测试用例？

**回答话术：**

我从三个方面管理测试用例：

**第一是分层分级**，用Pytest的mark标记用例优先级（P0、P1、P2）和类型（冒烟、回归、全量），执行时可以灵活选择。

```
@pytest.mark.smoke
@pytest.mark.P0
def test_login(self):
    pass
```

**第二是定期review**，接又变更后及时更新用例，删除过时的用例，补充新功能的用例。

**第三是数据驱动**，把测试数据和用例逻辑分离，修改数据不影响代码，降低维护成本。

每次迭代后，我会统计用例覆盖率和执行情况，持续优化用例集。

### _20._ 框架优化有哪些经验？

**回答话术：**

我总结了几个优化方向：

**性能优化**：使用Session复用连接，启用并发执行，缓存不变的数据（如token）。

**稳定性优化**：增加重试机制，优化等待策略，做好异常处理和兜底逻辑。

**可维护性优化**：遵循单一职责原则，每个类只做一件事；抽取公共方法，减少重复代码；规范命名和注释。 **可扩展性优化**：预留扩展点，比如支持插件化开发；使用设计模式，如工厂模式创建不同环境的配置对象。 **监控告警**：集成CI/CD后，失败自动通知；记录关键指标（成功率、响应时间），形成趋势图。

最重要的是持续迭代，根据团队反馈和实际问题不断改进框架。

## 二、Web自动化(中等)

_1._ 你在项目中使用的 _Web_ 自动化测试框架是什么？为什么选择它？

**回答话术：**

我使用的是 **Selenium + Pytest + POM模式** 的框架。

选择Selenium是因为它支持多浏览器，生态成熟，API简单易用，能满足大部分Web自动化需求。

Pytest作为测试框架，提供了强大的fixture和参数化功能，配合pytest-html可以生成详细的测试报告。

POM（Page Object Model）页面对象模型让页面元素和测试逻辑分离，页面变化时只需要修改PO类，不影响测试用例，维护成本低。

对于复杂场景，我也会结合Playwright，它执行速度更快，支持自动等待，截图和录屏功能更强大。

### _2._ 请描述你设计的 _Web_ 自动化测试框架的整体架构

**回答话术：**

我的框架采用分层架构，分为五层：

**第一层是Page层**，每个页面对应一个PO类，封装页面元素定位和操作方法。

**第二层是TestCase层**，编写测试用例，调用Page层的方法，只关注业务流程。

**第三层是Base层**，封装浏览器驱动初始化、公共操作方法如等待、截图、滚动等。

**第四层是Config层**，管理环境配置、浏览器类型、超时时间等参数。

**第五层是Data层**，管理测试数据，支持YAML、Excel等格式。

`project/ ├── pages/           #` 页面对象层 `├── testcases/       #` 测试用例层 `├── base/           #` 基础封装层 `├── config/         #` 配置管理层 `├── data/           #` 测试数据层 `└── reports/        #` 测试报告

这样设计职责清晰，易于维护和扩展。

### _3._ 什么是 _POM_ 模式？如何实现？

**回答话术：**

POM是Page Object Model页面对象模型，核心思想是把页面元素定位和操作封装到Page类中，测试用例只调用 Page类的方法。

优点是页面变化时只需修改PO类，用例不受影响，提高了代码复用性和可维护性。

```
class LoginPage:
```

```
    def __init__(self, driver):
        self.driver = driver
```

这样页面和用例解耦，维护起来非常方便。

_4. Selenium_ 中有哪些元素定位方式？你常用哪些？

**回答话术：**

Selenium提供8种定位方式：

**id、name、class_name、tag_name、link_text、partial_link_text、xpath、css_selector** 我常用的是：

**第一优先用id**，唯一且性能最好。

**第二用css_selector**，语法简洁，性能好，比如 `#id`、 `.class`、 `[name='value']`

**第三用xpath**，功能强大，可以通过文本、属性、层级关系定位，适合复杂场景。

`# CSS` 定位 `driver.find_element(By.CSS_SELECTOR, "#username") driver.find_element(By.CSS_SELECTOR, ".login-btn") # XPath` 定位 `driver.find_element(By.XPATH, "//input[@id='username']") driver.find_element(By.XPATH, "//button[text()='` 登录 `']") driver.find_element(By.XPATH, "//div[@class='header']//a[1]")`

尽量避免用tag_name和link_text，定位不准确容易出错。

### _5._ 如何处理页面元素定位不到的问题？

**回答话术：**

元素定位不到主要有三个原因：

**第一是元素还没加载出来**，我会用显式等待WebDriverWait，等待元素可见或可点击。

```
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
```

```
element = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "username"))
)
```

**第二是元素在iframe中**，需要先切换到iframe再定位。

`driver.switch_to.frame("iframeName") driver.find_element(By.ID, "element").click() driver.switch_to.default_content()  #` 切回主页面

**第三是定位表达式写错了**，我会在浏览器F12控制台验证xpath或css表达式是否正确。

在Base类中我封装了统一的元素查找方法，自动处理等待和异常。

### _6. Selenium_ 中的等待机制有哪些？如何选择？

**回答话术：**

Selenium有三种等待机制：

**强制等待sleep**：固定等待时间，不推荐使用，浪费时间且不灵活。

**隐式等待implicitly_wait**：全局设置，查找元素时如果没找到会等待设定时间再抛异常。

`driver.implicitly_wait(10)  #` 全局生效

**显式等待WebDriverWait**：针对特定元素设置等待条件，推荐使用。

```
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "submit"))
)
```

我的选择策略是：

**项目初期设置一个较小的隐式等待**，比如5秒兜底。

**针对关键元素或加载慢的元素用显式等待**，设置具体的等待条件，比如元素可见、可点击、文本包含等。 **不使用sleep**，除非是验证码倒计时这种必须等待的场景。

### _7._ 如何封装 _BasePage_ 基类？

**回答话术：**

我会创建一个BasePage基类，封装所有页面的公共操作方法：

```
class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
```

```
    def find_element(self, locator):
        """查找单个元素，自动等待"""
```

```
        """切换iframe"""
        iframe = self.find_element(locator)
        self.driver.switch_to.frame(iframe)

    def scroll_to_element(self, locator):
        """滚动到元素"""
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
```

所有PO类继承BasePage，就可以直接使用这些方法，避免重复代码。

### _8._ 如何处理浏览器驱动的管理？

**回答话术：**

我用webdriver-manager自动管理驱动，不需要手动下载和配置驱动路径。

`from selenium import webdriver from webdriver_manager.chrome import ChromeDriverManager from selenium.webdriver.chrome.service import Service #` 自动下载并使用匹配的 `ChromeDriver service = Service(ChromeDriverManager().install()) driver = webdriver.Chrome(service=service)`

在conftest.py中用fixture统一管理driver：

```
@pytest.fixture(scope="function")
def driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()
```

这样每个测试用例都能获得一个干净的浏览器实例，用完自动关闭。

支持通过配置文件切换浏览器类型，比如Chrome、Firefox、Edge。

### _9._ 如何处理弹窗（_alert_、 _confirm_、 _prompt_）？

**回答话术：**

Selenium处理JavaScript弹窗需要切换到alert对象：

`#` 等待 `alert` 出现

`alert = WebDriverWait(driver, 10).until(EC.alert_is_present()) #` 获取弹窗文本 `text = alert.text #` 确认弹窗 `alert.accept() #` 取消弹窗 `alert.dismiss() # prompt` 输入文本 `alert.send_keys("test") alert.accept()`

我在BasePage中封装了处理弹窗的方法：

```
def handle_alert(self, action="accept", text=None):
    alert = self.wait.until(EC.alert_is_present())
    if text:
        alert.send_keys(text)
    if action == "accept":
        alert.accept()
    else:
        alert.dismiss()
```

这样处理弹窗就很简单了。

### _10._ 如何处理文件上传和下载？

**回答话术：**

**文件上传** 有两种方式：

**第一种是input标签**，直接send_keys传文件路径。

```
upload_element = driver.find_element(By.ID, "fileUpload")
upload_element.send_keys("/path/to/file.txt")
```

**第二种是非input标签**，用AutoIt或pywinauto模拟Windows窗又操作。

**文件下载** 需要配置浏览器选项：

```
chrome_options = Options()
prefs = {
    "download.default_directory": "/path/to/download",
```

下载后需要等待文件下载完成，我会检查文件是否存在：

```
import time
def wait_for_download(file_path, timeout=30):
    for i in range(timeout):
        if os.path.exists(file_path):
            return True
        time.sleep(1)
    return False
```

### _11._ 如何处理动态元素（元素属性动态变化）？

**回答话术：**

动态元素主要有两种情况：

**第一种是元素id或class动态生成**，我会用相对稳定的属性定位，比如：

`#` 用部分匹配 `driver.find_element(By.XPATH, "//div[contains(@id, 'dynamic')]") driver.find_element(By.CSS_SELECTOR, "[id^='prefix']")  # id` 以 `prefix` 开头 `driver.find_element(By.CSS_SELECTOR, "[id$='suffix']")  # id` 以 `suffix` 结尾 `#` 用其他稳定属性

```
driver.find_element(By.XPATH, "//input[@name='username']")
```

**第二种是元素位置或内容动态变化**，我会通过父元素或兄弟元素定位，使用轴定位：

`#` 通过父元素定位 `driver.find_element(By.XPATH, "//div[@class='parent']//button[text()='` 提交 `']") #` 通过兄弟元素定位 `driver.find_element(By.XPATH, "//label[text()='` 用户名 `']/following-sibling::input")`

关键是找到页面中相对稳定的元素作为定位锚点。

### _12._ 如何处理表格数据的验证？

**回答话术：**

表格验证我主要用xpath遍历行和列：

 def get_table_data(driver, table_locator): """ 获取表格所有数据 """ table = driver.find_element(*table_locator) rows = table.find_elements(By.TAG_NAME, "tr") data = [] for row in rows[1:]:  # 跳过表头 cols = row.find_elements(By.TAG_NAME, "td") row_data = [col.text for col in cols] data.append(row_data) return data def find_in_table(driver, search_text): """ 在表格中查找指定内容 """ xpath = f"//table//td[text()='{search_text}']" return driver.find_elements(By.XPATH, xpath) # 获取特定单元格 cell = driver.find_element(By.XPATH, "//table/tbody/tr[2]/td[3]")  # 第 2 行第 3 列

对于复杂表格，我会把数据提取封装到PO类的方法中，用例只关注断言逻辑。

### _13._ 如何实现数据驱动测试？

#### **回答话术：**

我用pytest的parametrize结合外部数据文件实现数据驱动：

```
# data/login_data.yaml
test_data:
  - username: "admin"
    password: "123456"
    expected: "登录成功"
  - username: "admin"
    password: "wrong"
    expected: "密码错误"
# testcase
import yaml
def load_test_data():
    with open('data/login_data.yaml') as f:
        return yaml.safe_load(f)['test_data']
```

```
@pytest.mark.parametrize('data', load_test_data())
def test_login(driver, data):
    login_page = LoginPage(driver)
    login_page.login(data['username'], data['password'])
    assert data['expected'] in login_page.get_message()
```

这样测试数据和用例分离，非技术人员也能维护数据，扩展性强。

### _14._ 如何处理滑动验证码？

**回答话术：**

滑动验证码处理比较复杂，我主要用ActionChains模拟滑动：

 from selenium.webdriver import ActionChains def slide_verify(driver, slider_element, distance): """ 滑动验证码 """ action = ActionChains(driver) action.click_and_hold(slider_element)  # 按住滑块 action.move_by_offset(distance, 0)     # 水平移动 action.release()                        # 释放 action.perform()                        # 执行 # 或者分段滑动更像人工操作 def slide_verify_human_like(driver, slider, distance): action = ActionChains(driver) action.click_and_hold(slider) # 分段移动，模拟人工滑动 moved = 0 while moved < distance: x = random.randint(10, 20) action.move_by_offset(x, random.randint(-2, 2)) moved += x time.sleep(random.uniform(0.01, 0.05)) action.release().perform()

对于复杂的验证码，可以集成打码平台API或者用图像识别算法计算滑动距离。

测试环境建议让开发提供bypass机制，绕过验证码。

_15._ 如何实现失败截图和录屏？

**回答话术：**

我在conftest.py中用hook函数实现失败自动截图：

```
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # 获取driver
        driver = item.funcargs.get('driver')
        if driver:
            # 截图
            screenshot_path = f"screenshots/{item.name}.png"
            driver.save_screenshot(screenshot_path)

            # 附加到Allure报告
            with open(screenshot_path, 'rb') as f:
                allure.attach(f.read(), name="失败截图",
                            attachment_type=allure.attachment_type.PNG)
```

录屏我用opencv或者浏览器的cdp协议：

 # 使用 chrome 的录屏功能 from selenium.webdriver.common.action_chains import ActionChains driver.execute_cdp_cmd('Page.startScreencast', {}) # 测试执行 ... driver.execute_cdp_cmd('Page.stopScreencast', {})

失败截图对定位问题非常有帮助，特别是在CI环境中。

### _16._ 如何实现多浏览器兼容性测试？

**回答话术：**

我通过配置文件和fixture实现多浏览器支持：

```
# config.yaml
browser: chrome  # 可选chrome, firefox, edge
# conftest.py
@pytest.fixture(scope="function")
def driver(request):
    browser = request.config.getoption("--browser", default="chrome")

    if browser == "chrome":
        driver = webdriver.Chrome()
    elif browser == "firefox":
```

`driver = webdriver.Firefox() elif browser == "edge": driver = webdriver.Edge() driver.maximize_window() yield driver driver.quit() #` 命令行执行 `pytest --browser=firefox`

也可以用parametrize实现同一用例在多个浏览器上执行：

```
@pytest.fixture(params=["chrome", "firefox"])
def multi_browser(request):
    if request.param == "chrome":
        driver = webdriver.Chrome()
    else:
        driver = webdriver.Firefox()
    yield driver
    driver.quit()
```

结合Selenium Grid可以实现分布式并行测试。

### _17._ 如何处理页面跳转和新窗又切换？

#### **回答话术：**

Selenium处理多窗又需要切换句柄：

`#` 记录当前窗口句柄 `current_window = driver.current_window_handle #` 点击打开新窗口的链接 `driver.find_element(By.LINK_TEXT, "` 新窗口 `").click()`

`#` 获取所有窗口句柄 `all_windows = driver.window_handles #` 切换到新窗口 `for window in all_windows: if window != current_window: driver.switch_to.window(window) break #` 在新窗口操作 `... #` 关闭新窗口 `driver.close()`

`#` 切回原窗口 `driver.switch_to.window(current_window)`

我在BasePage中封装了窗又切换方法：

`def switch_to_new_window(self): """` 切换到最新打开的窗口 `""" self.driver.switch_to.window(self.driver.window_handles[-1])`

 def switch_to_window_by_title(self, title): """ 根据标题切换窗口 """ for handle in self.driver.window_handles: self.driver.switch_to.window(handle) if title in self.driver.title: return True return False

### _18._ 如何提高用例执行速度？

**回答话术：**

我从四个方面优化执行速度：

**第一是并发执行**，用pytest-xdist插件多进程运行。

`pytest -n 4 # 4` 个进程并发

**第二是减少等待时间**，用显式等待替代固定等待，设置合理的超时时间。

**第三是复用浏览器session**，用例间不重启浏览器，只清理cookie和缓存。

```
@pytest.fixture(scope="session")
def driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()
```

**第四是选择性执行**，用标签标记用例优先级，冒烟测试只跑P0用例。

`pytest -m "smoke" #` 只运行冒烟用例

通过这些优化，可以将执行时间缩短50%以上。

_19. Selenium_ 和 _Playwright_ 有什么区别？如何选择？

#### **回答话术：**

#### **Selenium的优势：**

- 生态成熟，文档丰富，社区活跃
- 支持多语言，团队容易上手
- 稳定性好，适合长期维护的项目

#### **Playwright的优势：**

- 执行速度更快，自动等待机制更智能
- 支持多标签页、多浏览器上下文
- 截图、录屏功能更强大
- 网络拦截和Mock更方便
- 支持移动端浏览器模拟

`# Playwright` 示例

```
from playwright.sync_api import sync_playwright
```

`with sync_playwright() as p: browser = p.chromium.launch() page = browser.new_page() page.goto("https://example.com") page.click("#submit")  #` 自动等待 `browser.close()`

#### **我的选择策略：**

新项目优先考虑Playwright

- 老项目维护继续用Selenium
- 复杂的网络场景用Playwright
- 简单的表单测试用Selenium

### _20. Web_ 自动化测试的最佳实践有哪些？

**回答话术：**

我总结了几点最佳实践：

**第一是元素定位稳定性**，优先用id，避免用xpath的绝对路径，多用相对定位。

**第二是遵循POM模式**，页面和用例分离，一个页面一个PO类。

**第三是合理使用等待**，用显式等待替代sleep，设置明确的等待条件。

**第四是做好断言**，不只断言元素存在，还要断言文本内容、属性值、页面跳转等。

**第五是失败处理机制**，失败自动截图、记录日志、支持失败重跑。

**第六是用例独立性**，每个用例独立运行，不依赖其他用例的执行结果。 **第七是持续维护**，页面变化及时更新PO类，定期review用例有效性。

**第八是合理的用例分层**，冒烟、回归、全量分开管理，CI只跑核心用例。

最重要的是根据项目特点灵活调整，没有完美的框架，只有合适的方案。

## 三、App自动化(低)

### _1._ 你在项目中使用的 _App_ 自动化测试框架是什么？为什么选择它？

**回答话术：**

我使用的是 **Appium + Pytest + POM模式** 的框架。

选择Appium是因为它跨平台，一套代码可以同时测试Android和iOS，基于WebDriver协议，API和Selenium类似，学习成本低。

Pytest提供了强大的测试管理能力，fixture机制可以很好地管理设备连接、应用启动等前置条件。

POM模式让页面元素和业务逻辑分离，页面改版时只需修改Page类，测试用例不受影响。

对于简单场景，我也会用uiautomator2，它是纯Python实现，执行速度更快，但只支持Android。

### _2._ 请描述你设计的 _App_ 自动化测试框架的整体架构

**回答话术：**

我的框架分为五层：

**第一层是Page层**，每个页面一个PO类，封装元素定位和操作方法。

**第二层是TestCase层**，编写测试场景，调用Page层方法。

**第三层是Base层**，封装driver初始化、公共操作如滑动、截图、等待等。 **第四层是Config层**，管理设备配置、desired_capabilities、包名等。

**第五层是Utils层**，提供日志、断言、数据处理等工具方法。

`project/ ├── pages/           #` 页面对象层 `├── testcases/       #` 测试用例层 `├── base/           #` 基础封装层 `├── config/         #` 配置管理层 `├── utils/          #` 工具类层 `└── reports/        #` 测试报告

这样设计职责清晰，支持Android和iOS双平台。

### _3. Appium_ 的核心原理是什么？如何与 _App_ 交互？

**回答话术：**

Appium是C/S架构，工作原理是：

**第一步，测试脚本发送HTTP请求** 到Appium Server。 **第二步，Appium Server解析请求**，转换为对应平台的自动化指令。 **第三步，Android平台通过UIAutomator2**，iOS平台通过XCUITest框架与App交互。 **第四步，操作结果返回给Appium Server**，再返回给测试脚本。

```
# desired_capabilities配置
caps = {
    "platformName": "Android",
    "deviceName": "emulator-5554",
    "appPackage": "com.example.app",
    "appActivity": ".MainActivity",
    "automationName": "UiAutomator2"
}
driver = webdriver.Remote('http://localhost:4723/wd/hub', caps)
```

Appium不需要修改App源码，通过底层框架实现自动化，这是它的核心优势。

_4. Android_ 和 _iOS_ 的元素定位方式有哪些？

**回答话术：**

**Android主要定位方式： resource-id**：唯一标识，优先使用，类似Web的id。 **accessibility id**：辅助功能id，对应content-desc属性。

**xpath**：功能强大但性能较差，复杂场景使用。

**uiautomator**：Android独有，支持UiSelector语法。

`# resource-id` 定位 `driver.find_element(AppiumBy.ID, "com.example:id/username")`

`# accessibility id` 定位 `driver.find_element(AppiumBy.ACCESSIBILITY_ID, "` 登录按钮 `")`

`# xpath` 定位 `driver.find_element(AppiumBy.XPATH, "//android.widget.Button[@text='` 登录 `']")`

`# uiautomator` 定位 `driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("` 登录 `")')`

**iOS主要定位方式：**

**accessibility id**：对应accessibility identifier。

**class name**：通过控件类型定位。

**predicate string**：iOS独有，类似SQL查询。 **class chain**：优化版的xpath。

优先用id，其次accessibility id，避免过度使用xpath。

### _5._ 如何获取 _App_ 的包名和启动 _Activity_？

**回答话术：**

有三种方式获取：

#### **第一种用aapt命令**：

`#` 获取包名和启动 `Activity aapt dump badging app.apk | grep package aapt dump badging app.apk | grep launchable-activity`

#### **第二种用adb命令**：

`#` 启动 `App` 后查看当前 `Activity adb shell dumpsys window | findstr mCurrentFocus`

`#` 或者 `adb logcat | grep ActivityManager`

**第三种用Python自动获取**：

```
import subprocess
```

```
def get_current_activity():
```

`cmd = "adb shell dumpsys window | grep mCurrentFocus" result = subprocess.getoutput(cmd) #` 解析包名和 `Activity return result`

我一般用aapt分析apk包，把配置写入config文件，自动化执行时直接读取。

### _6._ 如何设计 _BasePage_ 类封装公共操作？

**回答话术：**

我会在BasePage中封装所有页面的通用操作：

```
class BasePage:
    def __init__(self, driver):
        self.driver = driver
```

```
            if self.is_element_exist(locator):
                return True
            self.swipe_up()
        return False

    def take_screenshot(self, filename):
        """截图"""
        self.driver.save_screenshot(filename)
```

所有Page类继承BasePage，复用这些方法。

### _7._ 如何处理 _Toast_ 提示信息的获取？

**回答话术：**

Toast是Android的临时提示，需要特殊处理：

**方法一：使用xpath定位Toast**

```
def get_toast(driver, timeout=5):
    """获取Toast文本"""
```

#### **方法二：使用uiautomator定位uiautomator定位定位**

Toast时间很短，需要及时获取，建议在操作后立即断言。

### _8._ 如何实现滑动操作（上下左右滑动）？

**回答话术：**

滑动操作主要用swipe方法，需要计算坐标：

```
class SwipeUtil:
    def __init__(self, driver):
        self.driver = driver
        self.size = driver.get_window_size()
        self.width = self.size['width']
        self.height = self.size['height']

    def swipe_up(self, duration=1000):
        """向上滑动"""
        x = self.width * 0.5
        start_y = self.height * 0.8
        end_y = self.height * 0.2
        self.driver.swipe(x, start_y, x, end_y, duration)

    def swipe_down(self, duration=1000):
        """向下滑动"""
        x = self.width * 0.5
        start_y = self.height * 0.2
        end_y = self.height * 0.8
        self.driver.swipe(x, start_y, x, end_y, duration)

    def swipe_left(self, duration=1000):
        """向左滑动"""
        y = self.height * 0.5
        start_x = self.width * 0.8
        end_x = self.width * 0.2
        self.driver.swipe(start_x, y, end_x, y, duration)

    def swipe_right(self, duration=1000):
        """向右滑动"""
        y = self.height * 0.5
        start_x = self.width * 0.2
        end_x = self.width * 0.8
        self.driver.swipe(start_x, y, end_x, y, duration)
```

滑动距离和速度要合理，太快可能滑动失败，太慢影响执行效率。

### _9._ 如何处理 _WebView_ 和 _Native_ 切换？

**回答话术：**

混合App中需要在Native和WebView之间切换：

```
def switch_to_webview(driver, timeout=10):
```

```
    """切换到WebView"""
    # 等待WebView加载
    WebDriverWait(driver, timeout).until(
```

WebView中可以用Web元素定位方式，切换context是关键。

### _10._ 如何实现 _App_ 的安装、卸载和启动？

**回答话术：**

Appium和adb都可以实现：

#### **使用Appium的Desired Capabilities：**

 # 自动安装并启动 caps = { "platformName": "Android", "deviceName": "device_id", "app": "/path/to/app.apk",  # 自动安装 "noReset": False,  # 重置 App 数据 "fullReset": True,  # 卸载重装 } # 不安装，直接启动已安装的 App caps = { "appPackage": "com.example.app", "appActivity": ".MainActivity",

`"noReset": True,  #` 不重置，保留数据 `}`

#### **使用adb命令：**

```
import subprocess
def install_app(apk_path):
    """安装App"""
    cmd = f"adb install -r {apk_path}"  # -r覆盖安装
    subprocess.run(cmd, shell=True)
def uninstall_app(package_name):
    """卸载App"""
    cmd = f"adb uninstall {package_name}"
    subprocess.run(cmd, shell=True)
def start_app(package, activity):
    """启动App"""
    cmd = f"adb shell am start -n {package}/{activity}"
    subprocess.run(cmd, shell=True)
def stop_app(package):
    """关闭App"""
    cmd = f"adb shell am force-stop {package}"
    subprocess.run(cmd, shell=True)
```

自动化测试建议每次都重置App数据，保证用例独立性。

_11._ 如何处理权限弹窗（定位、相机、通知等）？

**回答话术：**

权限弹窗有两种处理方式：

**方法一：在代码中处理弹窗**

`def handle_permission_alert(driver): """` 处理权限弹窗 `""" try: # Android` 系统弹窗 `allow_btn = driver.find_element( AppiumBy.ID, "com.android.packageinstaller:id/permission_allow_button" ) allow_btn.click() except: pass #` 启动 `App` 后立即处理 `driver = webdriver.Remote('http://localhost:4723/wd/hub', caps)`

```
def handle_permission_alert(driver):
```

#### **方法二：通过Capabilities自动授权（推荐）**

```
caps = {
    "platformName": "Android",
    "appPackage": "com.example.app",
```

#### **方法三：通过adb预先授权**

```
adb shell pm grant com.example.app android.permission.CAMERA
adb shell pm grant com.example.app android.permission.ACCESS_FINE_LOCATION
```

推荐用autoGrantPermissions，简单可靠。

### _12._ 如何实现列表滑动查找元素？

**回答话术：**

列表滑动查找需要循环滑动直到找到目标元素：

 def find_element_by_swipe(driver, locator, max_swipes=10): """ 滑动查找元素 """ for i in range(max_swipes): try: element = driver.find_element(*locator) return element except: # 未找到，继续滑动 swipe_up(driver) raise Exception(f" 滑动 {max_swipes} 次仍未找到元素 ") def find_element_by_text(driver, text, max_swipes=10): """ 通过文本滑动查找 """ for i in range(max_swipes): try: element = driver.find_element( AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")' ) return element except: swipe_up(driver) return None

`#` 使用示例 `element = find_element_by_text(driver, "` 目标商品名称 `") element.click()`

注意要设置最大滑动次数，避免无限循环。

### _13._ 如何实现多设备并发测试？

#### **回答话术：**

多设备并发需要启动多个Appium Server，每个设备连接一个：

```
# conftest.py
import pytest
devices = [
    {"udid": "device1", "port": 4723},
```

#### **启动多个Appium Server：**

```
appium -p 4723 -bp 4724 -U device1
appium -p 4725 -bp 4726 -U device2
```

关键是端又号和systemPort不能冲突。

### _14._ 如何处理图片验证码？

**回答话术：**

图片验证码有三种处理方式：

#### **方法一：截图后OCR识别**

```
from PIL import Image
import pytesseract
def recognize_captcha(driver):
```

#### **方法二：集成打码平台**

```
def get_captcha_from_api(image_base64):
    """调用打码平台API"""
```

**方法三：测试环境绕过验证码**

让开发提供测试账号或万能验证码，这是最推荐的方式。

_15._ 如何实现 _Android_ 和 _iOS_ 双平台兼容？

**回答话术：**

通过配置和条件判断实现双平台兼容：

```
# config.yaml
android:
  platformName: Android
  deviceName: emulator-5554
  appPackage: com.example.app
  appActivity: .MainActivity
ios:
  platformName: iOS
  deviceName: iPhone 13
  bundleId: com.example.app
# base_page.py
class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.platform = driver.capabilities['platformName']

    def find_element_compatible(self, android_locator, ios_locator):
        """双平台元素定位"""
        if self.platform == 'Android':
            return self.driver.find_element(*android_locator)
        else:
            return self.driver.find_element(*ios_locator)
# page对象
class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        # 定义双平台元素
        if self.platform == 'Android':
            self.username_input = (AppiumBy.ID, "com.example:id/username")
        else:
            self.username_input = (AppiumBy.ACCESSIBILITY_ID, "username")

    def input_username(self, username):
        element = self.driver.find_element(*self.username_input)
        element.send_keys(username)
```

关键是抽象公共操作，差异化部分用条件判断。

### _16._ 如何实现失败重跑和失败截图？

**回答话术：**

使用pytest插件实现失败重跑和截图：

```
# conftest.py
```

```
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get('driver')
        if driver:
            # 失败截图
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshots/{item.name}_{timestamp}.png"
            driver.save_screenshot(screenshot_path)

            # 附加到Allure报告
            with open(screenshot_path, 'rb') as f:
                allure.attach(
                    f.read(),
                    name="失败截图",
                    attachment_type=allure.attachment_type.PNG
                )
# pytest.ini
[pytest]
reruns = 2  # 失败重跑2次
reruns_delay = 1  # 重跑间隔1秒
```

也可以对单个用例设置重跑：

```
@pytest.mark.flaky(reruns=3)
def test_unstable_feature(driver):
    pass
```

### _17._ 如何进行弱网络测试？

**回答话术：**

弱网络测试有两种方式：

**方法一：使用Appium的网络模拟**

`#` 设置网络类型 `driver.set_network_connection(6)  # 6` 表示 `WiFi+` 数据 `#` 网络类型常量 `# 0:` 无网络 `# 1:` 飞行模式 `# 2:` 仅 `WiFi # 4:` 仅数据 `# 6: WiFi+` 数据

`#` 断网测试

`driver.set_network_connection(0) #` 执行操作，验证无网络提示 `driver.set_network_connection(6)  #` 恢复网络

**方法二：使用Charles或Fiddler代理**

```
caps = {
    "platformName": "Android",
    "proxy": {
        "proxyType": "manual",
        "httpProxy": "192.168.1.100:8888",  # Charles代理地址
    }
}
```

在Charles中设置限速、丢包等弱网络场景。

**方法三：使用adb命令限速**

`#` 限制网速 `adb shell tc qdisc add dev wlan0 root netem delay 500ms`

### _18._ 如何获取 _App_ 性能数据（_CPU_、内存、流量）？

**回答话术：**

通过adb命令获取App性能数据：

```
import subprocess
class PerformanceMonitor:
```

```
                return f"{int(memory)/1024:.2f} MB"
```

 def get_network_usage(self): """ 获取网络流量 """ cmd = f"adb shell cat /proc/net/xt_qtaguid/stats | grep {self.package}" result = subprocess.getoutput(cmd) # 解析流量数据 return result # 使用示例 monitor = PerformanceMonitor("com.example.app") # 测试前记录基线 baseline_memory = monitor.get_memory_usage() # 执行测试 ... # 测试后对比 current_memory = monitor.get_memory_usage() assert current_memory < baseline_memory * 1.5 # 内存增长不超过 50%

#### 也可以用Appium的性能日志：

```
caps = {
    "enablePerformanceLogging": True
}
logs = driver.get_log('performance')
```

_19._ 如何实现 _App_ 启动时间测试？

**回答话术：**

#### 测试启动时间主要用adb命令：

```
import subprocess
import re
def measure_app_launch_time(package, activity):
    """测量App启动时间"""
    # 先关闭App
    subprocess.run(f"adb shell am force-stop {package}", shell=True)

    # 启动并获取时间
    cmd = f"adb shell am start -W -n {package}/{activity}"
    result = subprocess.getoutput(cmd)

    # 解析启动时间
    # TotalTime: 总启动时间
    total_time = re.findall(r'TotalTime: (\d+)', result)
    if total_time:
```

```
        return int(total_time[0])
    return None
# 多次测试取平均值
```

冷启动和热启动要分别测试。

### _20. App_ 自动化测试的最佳实践有哪些？

**回答话术：**

我总结了几点最佳实践：

**第一是元素定位稳定性**，优先用resource-id，避免用xpath的索引定位，多用text或content-desc。 **第二是等待机制**，用显式等待WebDriverWait，不用固定sleep，每个操作后等待页面稳定。

**第三是用例独立性**，每个用例独立运行，测试前reset App，清理数据，避免用例间依赖。 **第四是异常处理**，处理好权限弹窗、网络异常、崩溃等场景，失败自动截图记录现场。

**第五是POM模式**，页面元素和业务逻辑分离，一个页面一个PO类。

**第六是参数化数据驱动**，测试数据外部管理，支持批量执行。

**第七是CI集成**，连接真机或云测平台，定时执行冒烟测试，失败及时通知。 **第八是性能监控**，关注启动时间、内存、CPU，提前发现性能问题。 **第九是日志管理**，记录详细的操作日志和设备日志，便于问题定位。 **第十是合理分层**，冒烟、回归、专项测试分开管理，根据场景选择执行。 最重要的是根据项目特点灵活调整，持续优化框架。

测试开发训练营：针对面试求职的测试开发训练营，大厂导师 1v1 私教，帮助学员从 0 到 1 拿到测开满意的 offer

直播授课+实时互动答疑，课程到就业贯穿企业级案例，由测试开发导师全程主讲，绝无其他助理老
