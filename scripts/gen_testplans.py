#!/usr/bin/env python3
"""
Sinh 3 (+1) JMeter test plan cho Workflow 5:
  Login -> View Order History -> Browse Products -> Add to Cart -> Checkout

  python scripts/gen_testplans.py --student-id 2312xxxx [--date 20261119]

Ra: test-plans/{StudentID}_{Load|Stress|Spike|Soak}_{YYYYMMDD}.jmx
Mọi tham số tải đều là JMeter property (-J...) để chỉnh khi chạy, không cần sửa file.
"""
import argparse
import datetime as dt
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent


def x(s: str) -> str:
    return escape(str(s), {'"': "&quot;"})


# ---------------------------------------------------------------- primitives
def node(xml: str, children: str = "") -> str:
    return f"{xml}\n<hashTree>{children}</hashTree>\n"


def header_manager(name, headers):
    items = "".join(
        f'<elementProp name="" elementType="Header"><stringProp name="Header.name">{x(k)}</stringProp>'
        f'<stringProp name="Header.value">{x(v)}</stringProp></elementProp>'
        for k, v in headers
    )
    return node(
        f'<HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="{x(name)}" enabled="true">'
        f'<collectionProp name="HeaderManager.headers">{items}</collectionProp></HeaderManager>'
    )


def assert_code(code="200"):
    return node(
        f'<ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Assert HTTP {code}" enabled="true">'
        f'<collectionProp name="Asserion.test_strings"><stringProp name="0">{code}</stringProp></collectionProp>'
        '<stringProp name="Assertion.custom_message">HTTP status khác mong đợi (401/403 = sai credential/bị khóa/token; Non HTTP = lỗi kết nối/timeout)</stringProp>'
        '<stringProp name="Assertion.test_field">Assertion.response_code</stringProp>'
        '<boolProp name="Assertion.assume_success">false</boolProp>'
        '<intProp name="Assertion.test_type">8</intProp></ResponseAssertion>'
    )


def assert_json(path, expected=None, name=None):
    validate = expected is not None
    return node(
        f'<JSONPathAssertion guiclass="JSONPathAssertionGui" testclass="JSONPathAssertion" '
        f'testname="{x(name or "Assert " + path)}" enabled="true">'
        f'<stringProp name="JSON_PATH">{x(path)}</stringProp>'
        f'<stringProp name="EXPECTED_VALUE">{x(expected or "")}</stringProp>'
        f'<boolProp name="JSONVALIDATION">{str(validate).lower()}</boolProp>'
        '<boolProp name="EXPECT_NULL">false</boolProp><boolProp name="INVERT">false</boolProp>'
        '<boolProp name="ISREGEX">false</boolProp></JSONPathAssertion>'
    )


def json_extract(name, refs, paths, defaults):
    return node(
        f'<JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="{x(name)}" enabled="true">'
        f'<stringProp name="JSONPostProcessor.referenceNames">{x(";".join(refs))}</stringProp>'
        f'<stringProp name="JSONPostProcessor.jsonPathExprs">{x(";".join(paths))}</stringProp>'
        f'<stringProp name="JSONPostProcessor.match_numbers">{";".join("1" for _ in refs)}</stringProp>'
        f'<stringProp name="JSONPostProcessor.defaultValues">{x(";".join(defaults))}</stringProp>'
        '</JSONPostProcessor>'
    )


def jsr223_post(name, script):
    return node(
        f'<JSR223PostProcessor guiclass="TestBeanGUI" testclass="JSR223PostProcessor" testname="{x(name)}" enabled="true">'
        '<stringProp name="scriptLanguage">groovy</stringProp><stringProp name="parameters"></stringProp>'
        '<stringProp name="filename"></stringProp><stringProp name="cacheKey">true</stringProp>'
        f'<stringProp name="script">{x(script)}</stringProp></JSR223PostProcessor>'
    )


def http(name, method, path, body=None, children=""):
    body_xml = ""
    if body is not None:
        body_xml = (
            '<boolProp name="HTTPSampler.postBodyRaw">true</boolProp>'
            '<elementProp name="HTTPsampler.Arguments" elementType="Arguments"><collectionProp name="Arguments.arguments">'
            '<elementProp name="" elementType="HTTPArgument"><boolProp name="HTTPArgument.always_encode">false</boolProp>'
            f'<stringProp name="Argument.value">{x(body)}</stringProp><stringProp name="Argument.metadata">=</stringProp>'
            '</elementProp></collectionProp></elementProp>'
        )
    else:
        body_xml = (
            '<elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" '
            'testclass="Arguments"><collectionProp name="Arguments.arguments"/></elementProp>'
        )
    return node(
        f'<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="{x(name)}" enabled="true">'
        f'{body_xml}<stringProp name="HTTPSampler.domain"></stringProp><stringProp name="HTTPSampler.port"></stringProp>'
        f'<stringProp name="HTTPSampler.path">{x(path)}</stringProp>'
        f'<stringProp name="HTTPSampler.method">{method}</stringProp>'
        '<stringProp name="HTTPSampler.contentEncoding">UTF-8</stringProp>'
        '<boolProp name="HTTPSampler.follow_redirects">true</boolProp>'
        '<boolProp name="HTTPSampler.use_keepalive">true</boolProp></HTTPSamplerProxy>',
        children,
    )


def csv(name, file):
    return node(
        f'<CSVDataSet guiclass="TestBeanGUI" testclass="CSVDataSet" testname="{x(name)}" enabled="true">'
        f'<stringProp name="filename">{x(file)}</stringProp><stringProp name="fileEncoding">UTF-8</stringProp>'
        '<stringProp name="variableNames"></stringProp><boolProp name="ignoreFirstLine">false</boolProp>'
        '<stringProp name="delimiter">,</stringProp><boolProp name="quotedData">false</boolProp>'
        '<boolProp name="recycle">true</boolProp><boolProp name="stopThread">false</boolProp>'
        '<stringProp name="shareMode">shareMode.all</stringProp></CSVDataSet>'
    )


def timer(name, delay, rng):
    return node(
        f'<UniformRandomTimer guiclass="UniformRandomTimerGui" testclass="UniformRandomTimer" testname="{x(name)}" enabled="true">'
        f'<stringProp name="ConstantTimer.delay">{x(delay)}</stringProp>'
        f'<stringProp name="RandomTimer.range">{x(rng)}</stringProp></UniformRandomTimer>'
    )


def thread_group(name, threads, ramp, duration, delay, children, comment=""):
    return node(
        f'<ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="{x(name)}" enabled="true">'
        f'<stringProp name="TestPlan.comments">{x(comment)}</stringProp>'
        '<stringProp name="ThreadGroup.on_sample_error">startnextloop</stringProp>'
        '<elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" '
        'testclass="LoopController"><boolProp name="LoopController.continue_forever">false</boolProp>'
        '<stringProp name="LoopController.loops">-1</stringProp></elementProp>'
        f'<stringProp name="ThreadGroup.num_threads">{x(threads)}</stringProp>'
        f'<stringProp name="ThreadGroup.ramp_time">{x(ramp)}</stringProp>'
        '<boolProp name="ThreadGroup.scheduler">true</boolProp>'
        f'<stringProp name="ThreadGroup.duration">{x(duration)}</stringProp>'
        f'<stringProp name="ThreadGroup.delay">{x(delay)}</stringProp>'
        '<boolProp name="ThreadGroup.same_user_on_next_iteration">false</boolProp></ThreadGroup>',
        children,
    )


SAVE_CFG = (
    '<objProp><name>saveConfig</name><value class="SampleSaveConfiguration">'
    + "".join(
        f"<{t}>{v}</{t}>"
        for t, v in [
            ("time", "true"), ("latency", "true"), ("timestamp", "true"), ("success", "true"), ("label", "true"),
            ("code", "true"), ("message", "true"), ("threadName", "true"), ("dataType", "true"), ("encoding", "false"),
            ("assertions", "true"), ("subresults", "true"), ("responseData", "false"), ("samplerData", "false"),
            ("xml", "false"), ("fieldNames", "true"), ("responseHeaders", "false"), ("requestHeaders", "false"),
            ("responseDataOnError", "false"), ("saveAssertionResultsFailureMessage", "true"),
            ("assertionsResultsToSave", "0"), ("bytes", "true"), ("sentBytes", "true"), ("url", "true"),
            ("threadCounts", "true"), ("idleTime", "true"), ("connectTime", "true"),
        ]
    )
    + "</value></objProp>"
)


def listener(guiclass, name, errors_only=False):
    return node(
        f'<ResultCollector guiclass="{guiclass}" testclass="ResultCollector" testname="{x(name)}" enabled="true">'
        f'<boolProp name="ResultCollector.error_logging">{str(errors_only).lower()}</boolProp>{SAVE_CFG}'
        '<stringProp name="filename"></stringProp></ResultCollector>'
    )


# ---------------------------------------------------------------- workflow 5
# Ghi chú review: bản đầu dùng JSR223 Groovy để chuẩn hóa price (number/string – bug B8).
# Groovy 3/4 đi kèm JMeter 5.6.3 KHÔNG chạy trên JDK 25 ("Unsupported class file major version 69").
# JSON Extractor đã trả price không kèm dấu nháy cho cả 2 kiểu, nên dùng __jexl3 (thuần Java) để tính tổng.
CALC_SCRIPT = """// price có thể là number (id lẻ) hoặc string (id chẵn – bug B8) -> chuẩn hóa
try {
  long price = new BigDecimal(String.valueOf(vars.get("price"))).longValue()
  int qty = Integer.parseInt(vars.get("quantity"))
  vars.put("price_num", String.valueOf(price))
  vars.put("line_total", String.valueOf(price * qty))
} catch (Exception e) {
  vars.put("price_num", "0"); vars.put("line_total", "0")
  log.warn("Không tính được giá cho product " + vars.get("product_id") + ": " + e.message)
}"""

AUTH = lambda: header_manager("Bearer token", [("Authorization", "Bearer ${token}")])


def workflow():
    return (
        http("01 Login", "POST", "/api/login",
             '{"email":"${email}","password":"${password}"}',
             assert_code() + assert_json("$.token", name="Assert có JWT token")
             + json_extract("Extract token & user id", ["token", "user_id"], ["$.token", "$.user.id"], ["NOT_FOUND", "0"]))
        + http("02 View Order History", "GET", "/api/orders/my-orders", None,
               AUTH() + assert_code() + assert_json("$[0].user_id", "${user_id}", "Assert đơn thuộc đúng user")
               + json_extract("Extract history size", ["history_size"], ["$.length()"], ["0"]))
        + http("03 Browse Products", "GET", "/api/products", None,
               assert_code() + assert_json("$[0].id", name="Assert danh sách có sản phẩm"))
        + http("04 Search Products", "GET", "/api/products?search=${__urlencode(${keyword})}", None,
               assert_code() + assert_json("$[0].name", name="Assert có kết quả tìm kiếm"))
        + http("05 Product Detail", "GET", "/api/products/${product_id}", None,
               assert_code() + assert_json("$.id", name="Assert sản phẩm tồn tại (id sai vẫn trả 200 {})")
               + json_extract("Extract name & price", ["prod_name", "price"], ["$.name", "$.price"], ["NOT_FOUND", "0"]))
        + http("06 Add to Cart", "POST", "/api/cart",
               '{"id":${product_id},"name":"${prod_name}","price":${price},"quantity":${quantity}}',
               AUTH() + assert_code() + assert_json("$.message", "Added to cart"))
        + http("07 View Cart", "GET", "/api/cart", None,
               AUTH() + assert_code() + assert_json("$[0].id", name="Assert giỏ không rỗng"))
        + http("08 Checkout", "POST", "/api/checkout",
               '{"total_amount":${__jexl3(${price} * ${quantity})},"shipping_address":"${shipping_address}"}',
               AUTH() + assert_code() + assert_json("$.orderId", name="Assert tạo được orderId")
               + json_extract("Extract orderId", ["order_id"], ["$.orderId"], ["NOT_FOUND"]))
    )


def tg_children(think_min, think_range):
    return timer("Think time (Uniform Random)", think_min, think_range) + workflow()


def udv(pairs):
    items = "".join(
        f'<elementProp name="{k}" elementType="Argument"><stringProp name="Argument.name">{k}</stringProp>'
        f'<stringProp name="Argument.value">{x(v)}</stringProp><stringProp name="Argument.metadata">=</stringProp></elementProp>'
        for k, v in pairs
    )
    return (
        '<elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" '
        f'testclass="Arguments"><collectionProp name="Arguments.arguments">{items}</collectionProp></elementProp>'
    )


def test_plan(name, comment, thread_groups, report_listener, extra_vars=()):
    common = (
        node(
            '<ConfigTestElement guiclass="HttpDefaultsGui" testclass="ConfigTestElement" testname="HTTP Request Defaults" enabled="true">'
            '<elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments">'
            '<collectionProp name="Arguments.arguments"/></elementProp>'
            '<stringProp name="HTTPSampler.protocol">http</stringProp>'
            '<stringProp name="HTTPSampler.domain">${HOST}</stringProp><stringProp name="HTTPSampler.port">${PORT}</stringProp>'
            '<stringProp name="HTTPSampler.connect_timeout">5000</stringProp>'
            '<stringProp name="HTTPSampler.response_timeout">30000</stringProp></ConfigTestElement>'
        )
        + header_manager("JSON headers", [("Content-Type", "application/json; charset=UTF-8"), ("Accept", "application/json")])
        + csv("CSV – users (email,password,shipping_address)", "${DATA_DIR}/users.csv")
        + csv("CSV – products (product_id,quantity,keyword)", "${DATA_DIR}/products.csv")
    )
    body = common + thread_groups + report_listener
    vars_ = [("HOST", "${__P(host,localhost)}"), ("PORT", "${__P(port,3000)}"),
             ("DATA_DIR", "${__P(data_dir,../data)}"), *extra_vars]
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">\n<hashTree>\n'
        + node(
            f'<TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="{x(name)}" enabled="true">'
            f'<stringProp name="TestPlan.comments">{x(comment)}</stringProp>'
            '<boolProp name="TestPlan.functional_mode">false</boolProp>'
            '<boolProp name="TestPlan.serialize_threadgroups">false</boolProp>'
            '<boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>'
            + udv(vars_) + "</TestPlan>",
            body,
        )
        + "</hashTree>\n</jmeterTestPlan>\n"
    )


# ---------------------------------------------------------------- scenarios
def load_plan(name):
    tg = thread_group(
        "Load – ${__P(users,50)} VU steady", "${__P(users,50)}", "${__P(rampup,60)}", "${__P(duration,360)}", "0",
        tg_children("${__P(think_min,1000)}", "${__P(think_range,2000)}"),
        "Tải bình thường: 50 VU, ramp-up 60s (~1 VU/1.2s), giữ ~5 phút, think-time 1–3s.",
    )
    return test_plan(name, "Workflow 5 – LOAD. Listener: Summary Report.", tg, listener("SummaryReport", "Summary Report"))


def stress_plan(name):
    tgs = ""
    step, step_len, steps = "${__P(step_users,100)}", 90, 5
    total = step_len * steps
    for i in range(steps):
        tgs += thread_group(
            f"Stress step {i + 1} (+{{step}} VU @ {i * step_len}s)".replace("{step}", "${__P(step_users,100)}"),
            step, "${__P(step_ramp,30)}", str(total - i * step_len), str(i * step_len),
            tg_children("${__P(think_min,300)}", "${__P(think_range,700)}"),
            f"Bậc {i + 1}/{steps}: cộng thêm step_users VU tại t={i * step_len}s, giữ tới t={total}s.",
        )
    return test_plan(
        name, "Workflow 5 – STRESS bậc thang 100→500 VU (mỗi bậc 90s), think-time 0.3–1s. Listener: Aggregate Report.",
        tgs, listener("StatVisualizer", "Aggregate Report"),
    )


def spike_plan(name):
    tgs = thread_group(
        "Spike – baseline ${__P(base_users,20)} VU", "${__P(base_users,20)}", "10", "${__P(duration,300)}", "0",
        tg_children("${__P(think_min,1000)}", "${__P(think_range,1000)}"),
        "Nền 20 VU suốt 300s.",
    ) + thread_group(
        "Spike – burst ${__P(spike_users,300)} VU", "${__P(spike_users,300)}", "${__P(spike_ramp,5)}",
        "${__P(spike_hold,60)}", "${__P(spike_at,120)}",
        tg_children("${__P(think_min,1000)}", "${__P(think_range,1000)}"),
        "Đột biến: +300 VU trong 5s tại t=120s, giữ 60s rồi tắt → quan sát hồi phục t=180–300s.",
    )
    return test_plan(
        name, "Workflow 5 – SPIKE 20 → 320 VU → 20. Listener: View Results Tree (chỉ lỗi).",
        tgs, listener("ViewResultsFullVisualizer", "View Results Tree (errors only)", errors_only=True),
    )


def soak_plan(name):
    tg = thread_group(
        "Soak – ${__P(users,400)} VU / ${__P(duration,900)}s", "${__P(users,400)}", "${__P(rampup,60)}",
        "${__P(duration,900)}", "0", tg_children("${__P(think_min,300)}", "${__P(think_range,700)}"),
        "Endurance 15 phút ở ~65-70% throughput ổn định tối đa (~950 RPS, tìm được từ Stress breakpoint) ≈ 600 RPS.",
    )
    return test_plan(name, "Workflow 5 – SOAK/Endurance. Listener: Simple Data Writer.", tg,
                     listener("SimpleDataWriter", "Simple Data Writer"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--student-id", required=True)
    ap.add_argument("--date", default=dt.date.today().strftime("%Y%m%d"))
    a = ap.parse_args()
    out = ROOT / "test-plans"
    out.mkdir(exist_ok=True)
    for kind, fn in [("Load", load_plan), ("Stress", stress_plan), ("Spike", spike_plan), ("Soak", soak_plan)]:
        fname = f"{a.student_id}_{kind}_{a.date}"
        (out / f"{fname}.jmx").write_text(fn(fname), encoding="utf-8")
        print("wrote", out / f"{fname}.jmx")
