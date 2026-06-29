import openpyxl
from copy import copy

wb = openpyxl.load_workbook(r'D:\测试用例\20260611测试用例\携程协议.xlsx')
ws = wb.active

# Col indexes (1-based): A=1=STORY, B=2=节点, C=3=用例名称, D=4=摘要, E=5=前置条件, F=6=执行步骤, G=7=预期结果, H=8=实际, I=9=优先级, J=10=作者, K=11=类型, L=12=回归, M=13=应用, N=14=标签

# ===== Flow reference =====
# 新模式授信: 提交授信→instance落库(file_id)+mode_record落库→aps下载→授信上送下游→终态→notice_info(INIT)→定时任务→notice_info(SUCCESS)→IMgp调downLoadPartnerAgreement→ags_status=SUCCESS
# 旧模式授信: 提交授信→有协议落库instance(不做判断)→上送LPS→lps调ags保存协议
# 借款类似

def set_cell(ws, row, col, value):
    """Set cell value, preserving existing formatting"""
    cell = ws.cell(row=row, column=col)
    cell.value = value

# ===== ROW 2: 新模式-新携程进件提交-触发协议拉取 =====
set_cell(ws, 2, 5, '1. aps_stg3.partner_agreement_config表：partner_code=XCtrip, enabled=Y, grayscale_ratio>1000，状态为NORMAL\n2. 携程渠道新用户（partner_agreement_mode_record表中无该用户的老模式记录）\n3. 携程侧该授信用户在授信环节有4个已签署的协议文件且提供了auth_code')
set_cell(ws, 2, 6, '1. 调用携程授信进件提交接口（传auth_code和协议相关信息）\n2. 查询aps_stg3.partner_agreement_instance表\n3. 查询aps_stg3.partner_agreement_mode_record表\n4. 查看lps日志确认是否调用ags协议服务')
set_cell(ws, 2, 7, '1. 授信进件提交成功，接口返回成功\n2. partner_agreement_instance表落库4条协议记录，file_id字段不为空，status=INIT\n3. partner_agreement_mode_record表插入1条记录，记录当前用户走的模式为NEW\n4. lps日志中无调用ags协议服务的记录（协议由携程侧生成）')

# ===== ROW 3: 新模式-进件提交-协议缺失触发失败场景 =====
set_cell(ws, 3, 5, '1. aps_stg3.partner_agreement_config表：partner_code=XCtrip, enabled=Y, grayscale_ratio>1000\n2. 携程渠道新用户，但携程侧授信环节无已签署的协议文件（未传auth_code或auth_code无效）')
set_cell(ws, 3, 6, '1. 调用携程授信进件提交接口（无协议或auth_code缺失）\n2. 查询aps.order_info表\n3. 查询user_order_notice_info表\n4. 查询partner_agreement_instance表')
set_cell(ws, 3, 7, '1. 授信进件提交成功但交易被拒绝\n2. aps.order_info状态变更为ARJ（拒绝）\n3. user_order_notice_info表无记录（不发送通知）\n4. partner_agreement_instance表无记录（协议缺失不落库）')

# ===== ROW 4: (空名) timeout超时场景 =====
set_cell(ws, 4, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y, timeout_minutes设为较短值（如2分钟）\n2. 携程渠道新用户，模拟协议拉取全部超时')
set_cell(ws, 4, 6, '1. 修改partner_agreement_config.timeout_minutes为2\n2. 调用携程授信进件提交接口（协议拉取全部超时，超过timeout_minutes未返回）\n3. 查询aps.order_info表\n4. 查询user_order_notice_info表')
set_cell(ws, 4, 7, '1. 授信进件提交成功但交易被拒绝（超时触发拒绝，不阻塞主流程）\n2. aps.order_info状态变更为ARJ（拒绝）\n3. user_order_notice_info表无记录')

# ===== ROW 5: 新模式-进件提交-定时任务补偿 =====
set_cell(ws, 5, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y，max_retry_interval_minutes和fast_retry_window_minutes/fast_retry_interval_minutes已配置\n2. partner_agreement_instance表中存在status=FAIL且retry_count未达上限的记录')
set_cell(ws, 5, 6, '1. 确认partner_agreement_instance表有拉取失败待补拉的记录（status=FAIL）\n2. 等待定时任务（快速补拉窗口内fast_retry_interval_minutes间隔）触发补拉\n3. 查询partner_agreement_instance表')
set_cell(ws, 5, 7, '1. 定时任务触发补拉成功\n2. partner_agreement_instance表对应记录status变为SUCCESS，file_id更新为协议文件ID')

# ===== ROW 6: 新模式-360API老户重授信-触发协议拉取 =====
set_cell(ws, 6, 5, '1. aps_stg3.partner_agreement_config表：partner_code=XCtrip, enabled=Y, grayscale_ratio>1000\n2. 携程渠道老用户（partner_agreement_mode_record表中有该用户的OLD模式记录）\n3. 走360API老链路，携程侧授信环节有4个已签署的协议文件')
set_cell(ws, 6, 6, '1. 通过360API老链路调用携程授信进件提交接口\n2. 查询aps_stg3.partner_agreement_instance表\n3. 查询aps_stg3.partner_agreement_mode_record表\n4. 查看APS日志确认是否调用ags协议服务')
set_cell(ws, 6, 7, '1. 授信进件提交成功\n2. partner_agreement_instance表落库4条协议记录，file_id不为空，status=INIT\n3. partner_agreement_mode_record表插入1条记录，记录当前用户走的模式为NEW\n4. APS日志中无调用ags协议服务的记录（老户走新模式，协议由携程侧生成）')

# ===== ROW 7: 新模式-授信终态后通知imgp拉取协议 =====
set_cell(ws, 7, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y\n2. 授信进件已提交成功，协议已落库partner_agreement_instance（status=INIT, file_id不为空）\n3. partner_agreement_mode_record已记录当前用户为NEW模式\n4. aps已根据授信接口参数中的链接下载协议成功')
set_cell(ws, 7, 6, '1. 授信上送到下游，授信到终态（通过/拒绝）\n2. 查询aps.user_order_notice_info表\n3. 等待定时任务拉起通知IMgp\n4. 查询aps-app日志确认IMgp调用downLoadPartnerAgreement接口\n5. 查询partner_agreement_instance表ags_status字段')
set_cell(ws, 7, 7, '1. aps.user_order_notice_info表插入1条记录，状态为INIT\n2. 定时任务拉起通知IMgp后，user_order_notice_info表状态变为SUCCESS\n3. aps-app日志中有IMgp调用downLoadPartnerAgreement接口的记录\n4. partner_agreement_instance.ags_status变为SUCCESS（协议拉取完成）')

# ===== ROW 8: (空名) 授信拒绝通知 =====
set_cell(ws, 8, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y\n2. 授信进件已提交，协议已落库，但授信终态为拒绝')
set_cell(ws, 8, 6, '1. 授信到终态为拒绝\n2. 查询aps.user_order_notice_info表\n3. 查询partner_agreement_instance表ags_status')
set_cell(ws, 8, 7, '1. aps.user_order_notice_info表插入1条记录（记录拒绝结果），状态INIT→SUCCESS\n2. partner_agreement_instance.ags_status仍为INIT（授信拒绝不触发协议下载）\n3. aps-app日志中无downLoadPartnerAgreement调用')

# ===== ROW 9: (空名) 协议拉取成功但授信失败 =====
set_cell(ws, 9, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y\n2. 授信进件协议拉取成功（partner_agreement_instance.status=INIT, file_id不为空），但后续授信上送下游失败')
set_cell(ws, 9, 6, '1. 调用授信进件提交接口（协议拉取成功）\n2. 模拟授信上送下游失败\n3. 查询partner_agreement_instance表\n4. 查询user_order_notice_info表')
set_cell(ws, 9, 7, '1. partner_agreement_instance表协议记录保持INIT状态，file_id不为空（协议已保存）\n2. user_order_notice_info表无记录（授信未到终态）\n3. 已落库的协议记录不受授信失败影响')

# ===== ROW 10: 新模式-借款提交-老链路协议拉取(版本1) =====
set_cell(ws, 10, 5, '1. aps_stg3.partner_agreement_config表：partner_code=XCtrip, enabled=Y, config_version_id为版本1\n2. partner_agreement_item_config表fetch_node=借款环节，协议配置为3条\n3. 授信已完成，用户有借款额度\n4. 携程侧借款环节有3个已签署的协议文件')
set_cell(ws, 10, 6, '1. 调用携程借款提交接口（含协议编号contract_no参数）\n2. 查询aps_stg3.partner_agreement_instance表\n3. 查询aps.order_iou表\n4. 查看tfs日志确认是否调用ags协议服务')
set_cell(ws, 10, 7, '1. 借款提交成功\n2. partner_agreement_instance表落库3条协议记录，file_id不为空，status=INIT，contract_no不为空\n3. aps.order_iou表有借款记录\n4. tfs日志中无调用ags协议服务的记录')

# ===== ROW 11: (空名) 版本2 =====
set_cell(ws, 11, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y, config_version_id为版本2\n2. partner_agreement_item_config表借款环节协议配置为4条\n3. 授信已完成，携程侧借款环节有4个已签署的协议文件')
set_cell(ws, 11, 6, '1. 调用携程借款提交接口\n2. 查询aps_stg3.partner_agreement_instance表\n3. 查询aps.order_iou表\n4. 查看tfs日志确认是否调用ags协议服务')
set_cell(ws, 11, 7, '1. 借款提交成功\n2. partner_agreement_instance表落库4条协议记录，file_id不为空，status=INIT\n3. aps.order_iou表有借款记录\n4. tfs日志中无调用ags协议服务的记录')

# ===== ROW 12: 新模式-借款提交-协议缺失触发失败 =====
set_cell(ws, 12, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y\n2. 授信已完成，但携程侧借款环节无已签署的协议文件')
set_cell(ws, 12, 6, '1. 调用携程借款提交接口（借款环节协议缺失）\n2. 查询aps.order_iou表\n3. 查询user_order_notice_info表\n4. 查询partner_agreement_instance表')
set_cell(ws, 12, 7, '1. 借款提交成功但交易被拒绝\n2. aps.order_iou表state为9（拒绝）\n3. user_order_notice_info表无记录\n4. partner_agreement_instance表无借款协议记录')

# ===== ROW 13: (空名) 借款超时 =====
set_cell(ws, 13, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y, timeout_minutes设为2\n2. 授信已完成，模拟借款环节协议拉取全部超时')
set_cell(ws, 13, 6, '1. 修改partner_agreement_config.timeout_minutes为2\n2. 调用携程借款提交接口（协议拉取全部超时，超过timeout_minutes未返回）\n3. 查询aps.order_iou表\n4. 查询user_order_notice_info表')
set_cell(ws, 13, 7, '1. 借款提交成功但交易被拒绝（超时触发拒绝）\n2. aps.order_iou表state为9（拒绝）\n3. user_order_notice_info表无记录')

# ===== ROW 14: 新模式-借款终态-放款通知触发协议下载 =====
set_cell(ws, 14, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y\n2. 借款已提交成功，协议已落库partner_agreement_instance（status=INIT, file_id不为空）\n3. aps已根据借款接口参数中的链接下载协议成功')
set_cell(ws, 14, 6, '1. 借款到终态（放款通过）\n2. 查询aps.user_order_notice_info表\n3. 等待定时任务拉起通知IMgp\n4. 查询aps-app日志确认IMgp调用downLoadPartnerAgreement接口\n5. 查询partner_agreement_instance表ags_status字段')
set_cell(ws, 14, 7, '1. aps.user_order_notice_info表插入1条记录，状态为INIT\n2. 定时任务拉起通知IMgp后，user_order_notice_info表状态变为SUCCESS\n3. aps-app日志中有IMgp调用downLoadPartnerAgreement接口的记录\n4. partner_agreement_instance.ags_status变为SUCCESS')

# ===== ROW 15: (空名) 借款放款拒绝 =====
set_cell(ws, 15, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y\n2. 借款已提交，协议已落库，但借款终态为放款拒绝')
set_cell(ws, 15, 6, '1. 借款到终态为放款拒绝\n2. 查询aps.user_order_notice_info表\n3. 查询partner_agreement_instance表ags_status')
set_cell(ws, 15, 7, '1. aps.user_order_notice_info表插入1条记录（记录拒绝结果），状态INIT→SUCCESS\n2. partner_agreement_instance.ags_status仍为INIT（放款拒绝不触发协议下载）')

# ===== ROW 16: (空名) 借款放款成功但协议下载失败 =====
set_cell(ws, 16, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y\n2. 借款放款通过，但IMgp调用downLoadPartnerAgreement接口失败')
set_cell(ws, 16, 6, '1. 借款放款通过，user_order_notice_info表生成INIT记录\n2. 定时任务通知IMgp，但downLoadPartnerAgreement调用失败\n3. 查询partner_agreement_instance表ags_status\n4. 触发协议补拉定时任务')
set_cell(ws, 16, 7, '1. user_order_notice_info表记录状态为SUCCESS（通知已发送）\n2. partner_agreement_instance.ags_status保持INIT（下载失败）\n3. 补拉定时任务可重试，重试成功后ags_status变为SUCCESS')

# ===== ROW 17: (空名) 协议拉取成功但放款失败 =====
set_cell(ws, 17, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y\n2. 借款协议拉取成功（partner_agreement_instance.file_id不为空），但后续放款失败')
set_cell(ws, 17, 6, '1. 调用借款提交接口（协议拉取成功）\n2. 模拟放款失败\n3. 查询partner_agreement_instance表')
set_cell(ws, 17, 7, '1. partner_agreement_instance表协议记录保持INIT状态，file_id不为空\n2. 放款失败不影响已落库的协议记录')

# ===== ROW 18: 新模式-借款发送转出中 =====
set_cell(ws, 18, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y\n2. 借款提交后订单状态为转出中（需转中继后提交借款），协议未拉取完成')
set_cell(ws, 18, 6, '1. 提交借款，订单进入转出中状态\n2. 协议拉取未完成时转出中到期\n3. 查询aps.order_iou表')
set_cell(ws, 18, 7, '1. 借款提交成功但被拒绝\n2. aps.order_iou表state为9（拒绝）')

# ===== ROW 19: 新模式-借款节点聚合流程 =====
set_cell(ws, 19, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y\n2. 借款提交完成，需走过放款+协议下载聚合流程')
set_cell(ws, 19, 6, '1. 执行借款聚合流程（放款+协议下载串联处理）\n2. 查询user_order_notice_info表\n3. 查询partner_agreement_instance表ags_status')
set_cell(ws, 19, 7, '1. 借款聚合流程执行完成\n2. 放款通知和协议下载联动正确\n3. partner_agreement_instance.ags_status变为SUCCESS')

# ===== ROW 20: 新模式-签章完成后拉取协议 =====
set_cell(ws, 20, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y\n2. 放款通过，IMgp已调用downLoadPartnerAgreement成功拉取协议\n3. 用户已完成签署')
set_cell(ws, 20, 6, '1. 放款通过后用户签署完成\n2. 调用已签章协议拉取接口\n3. 验证拉取的协议文件含用户电子签章')
set_cell(ws, 20, 7, '1. 已签章协议拉取成功，返回协议文件\n2. 协议文件含用户电子签章，内容可正常预览')

# ===== ROW 21: (空名) 放款拒绝用户签署后拉取 =====
set_cell(ws, 21, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y\n2. 借款放款被拒绝，用户已签署协议')
set_cell(ws, 21, 6, '1. 放款拒绝\n2. 用户完成签署\n3. 调用已签章协议拉取接口')
set_cell(ws, 21, 7, '1. 已签章协议拉取成功，返回协议文件\n2. 放款拒绝不影响已签章协议的拉取')

# ===== ROW 22: (空名) 放款成功但协议下载失败后签署拉取 =====
set_cell(ws, 22, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y\n2. 放款通过但downLoadPartnerAgreement调用失败，ags_status未变为SUCCESS')
set_cell(ws, 22, 6, '1. 放款通过但协议下载失败\n2. 用户完成签署\n3. 调用已签章协议拉取接口')
set_cell(ws, 22, 7, '1. 已签章协议拉取失败（协议文件尚未下载成功）\n2. 需等待协议补拉成功后方可拉取已签章协议')

# ===== ROW 23: (空名) 协议拉取成功但放款失败后签署拉取 =====
set_cell(ws, 23, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y\n2. 协议拉取成功但放款失败，用户已签署协议')
set_cell(ws, 23, 6, '1. 协议拉取成功，放款失败\n2. 用户完成签署\n3. 调用已签章协议拉取接口')
set_cell(ws, 23, 7, '1. 已签章协议拉取成功，返回协议文件\n2. 协议拉取成功不受放款失败影响')

# ===== ROW 24: 高登模式-提交进件通过(旧模式) =====
set_cell(ws, 24, 5, '1. aps_stg3.partner_agreement_config表：partner_code=XCtrip, enabled=N, grayscale_ratio>1000（灰度关闭），状态NORMAL\n2. 携程渠道测试账号')
set_cell(ws, 24, 6, '1. 调用携程授信进件提交接口\n2. 查询partner_agreement_instance表\n3. 查询partner_agreement_mode_record表\n4. 查看lps日志确认是否调用ags协议服务')
set_cell(ws, 24, 7, '1. 授信进件提交成功，走原有流程\n2. partner_agreement_instance表：有传协议则落库（不做任何判断，下载失败也不管），无传协议则不落库\n3. partner_agreement_mode_record表插入1条记录，模式为OLD\n4. lps日志中有调用ags接口保存协议的记录（协议由ags生成）\n5. user_order_notice_info表无记录（旧模式不触发IMgp通知）')

# ===== ROW 25: 高登模式-提交借款并放款成功(旧模式) =====
set_cell(ws, 25, 5, '1. aps_stg3.partner_agreement_config表：enabled=N, grayscale_ratio>1000\n2. 授信进件已完成（旧模式）\n3. 携程侧借款环节有传协议')
set_cell(ws, 25, 6, '1. 调用携程借款提交接口\n2. 查询partner_agreement_instance表\n3. 查询user_order_notice_info表\n4. 查看tfs日志确认是否调用ags协议服务')
set_cell(ws, 25, 7, '1. 借款提交成功，走原有流程\n2. partner_agreement_instance表：有传协议则落库（仅落库不判断），无则不落库\n3. tfs日志中有调用ags接口保存协议的记录\n4. user_order_notice_info表无记录（旧模式不触发IMgp通知）')

# ===== ROW 26: 灰度控制-灰度比例 =====
set_cell(ws, 26, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y, grayscale_ratio=1001（全量走旧模式），状态NORMAL\n2. 携程渠道测试账号')
set_cell(ws, 26, 6, '1. 设置partner_agreement_config.grayscale_ratio=1001（灰度全关）\n2. 调用携程授信进件提交接口\n3. 查询partner_agreement_mode_record表\n4. 查看lps日志')
set_cell(ws, 26, 7, '1. 授信进件提交成功，走高登模式（旧流程）\n2. partner_agreement_mode_record表记录模式为OLD\n3. lps日志中有调用ags协议服务的记录\n4. user_order_notice_info表无记录')

# ===== ROW 27: (空名) 灰度比例-借款 =====
set_cell(ws, 27, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y, grayscale_ratio=1001\n2. 授信已完成（旧模式）')
set_cell(ws, 27, 6, '1. 调用携程借款提交接口\n2. 查询partner_agreement_mode_record表\n3. 查看tfs日志')
set_cell(ws, 27, 7, '1. 借款提交成功，走高登模式（旧流程）\n2. partner_agreement_mode_record表记录模式为OLD\n3. tfs日志中有调用ags协议服务的记录\n4. user_order_notice_info表无记录')

# ===== ROW 28-29: 手机号白名单 =====
set_cell(ws, 28, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y, grayscale_ratio>1000, mobile_whitelist含指定手机号\n2. 该手机号对应的携程渠道用户')
set_cell(ws, 28, 6, '1. 以白名单手机号用户调用携程授信进件提交接口\n2. 查询partner_agreement_mode_record表\n3. 查询partner_agreement_instance表\n4. 查看lps日志')
set_cell(ws, 28, 7, '1. 白名单用户走新模式\n2. partner_agreement_mode_record表记录模式为NEW\n3. partner_agreement_instance表有协议记录\n4. lps日志中无ags协议调用')

set_cell(ws, 29, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y, grayscale_ratio>1000, mobile_whitelist含指定手机号\n2. 授信已完成（新模式），该手机号用户有借款额度')
set_cell(ws, 29, 6, '1. 以白名单手机号用户调用携程借款提交接口\n2. 查询partner_agreement_mode_record表\n3. 查询partner_agreement_instance表\n4. 查看tfs日志')
set_cell(ws, 29, 7, '1. 白名单用户借款走新模式\n2. partner_agreement_mode_record表记录模式为NEW\n3. partner_agreement_instance表有协议记录\n4. tfs日志中无ags协议调用')

# ===== ROW 30-31: 身份证号白名单 =====
set_cell(ws, 30, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y, grayscale_ratio>1000, id_number_whitelist含指定身份证号\n2. 该身份证号对应的携程渠道用户')
set_cell(ws, 30, 6, '1. 以白名单身份证号用户调用携程授信进件提交接口\n2. 查询partner_agreement_mode_record表\n3. 查询partner_agreement_instance表\n4. 查看lps日志')
set_cell(ws, 30, 7, '1. 白名单用户走新模式\n2. partner_agreement_mode_record表记录模式为NEW\n3. partner_agreement_instance表有协议记录\n4. lps日志中无ags协议调用')

set_cell(ws, 31, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y, grayscale_ratio>1000, id_number_whitelist含指定身份证号\n2. 授信已完成（新模式），该身份证号用户有借款额度')
set_cell(ws, 31, 6, '1. 以白名单身份证号用户调用携程借款提交接口\n2. 查询partner_agreement_mode_record表\n3. 查询partner_agreement_instance表\n4. 查看tfs日志')
set_cell(ws, 31, 7, '1. 白名单用户借款走新模式\n2. partner_agreement_mode_record表记录模式为NEW\n3. partner_agreement_instance表有协议记录\n4. tfs日志中无ags协议调用')

# ===== ROW 32-33: order_no白名单 =====
set_cell(ws, 32, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y, grayscale_ratio>1000, order_no_whitelist含指定order_no\n2. 该order_no对应的携程渠道用户')
set_cell(ws, 32, 6, '1. 以白名单order_no调用携程授信进件提交接口\n2. 查询partner_agreement_mode_record表\n3. 查询partner_agreement_instance表\n4. 查看lps日志')
set_cell(ws, 32, 7, '1. 白名单订单走新模式\n2. partner_agreement_mode_record表记录模式为NEW\n3. partner_agreement_instance表有协议记录\n4. lps日志中无ags协议调用')

set_cell(ws, 33, 5, '1. aps_stg3.partner_agreement_config表：enabled=Y, grayscale_ratio>1000, order_no_whitelist含指定order_no\n2. 授信已完成（新模式），该order_no对应的借款订单')
set_cell(ws, 33, 6, '1. 以白名单order_no调用携程借款提交接口\n2. 查询partner_agreement_mode_record表\n3. 查询partner_agreement_instance表\n4. 查看tfs日志')
set_cell(ws, 33, 7, '1. 白名单订单借款走新模式\n2. partner_agreement_mode_record表记录模式为NEW\n3. partner_agreement_instance表有协议记录\n4. tfs日志中无ags协议调用')

# Save
wb.save(r'D:\测试用例\20260611测试用例\携程协议.xlsx')
print('Done! Modified 32 rows (rows 2-33).')
print('Key fixes applied:')
print('  1. partner_agreement_config → DB表字段(enabled/grayscale_ratio/timeout_minutes/whitelists)')
print('  2. 补全 partner_agreement_mode_record 落库校验')
print('  3. 新户查lps日志无ags，老户(360API)查APS日志无ags')
print('  4. 授信：授信通知/授信拒绝；借款：放款通知/放款拒绝')
print('  5. 协议下载验证：user_order_notice_info INIT→SUCCESS → IMgp调downLoadPartnerAgreement → ags_status=SUCCESS')
print('  6. 旧模式：有协议就落库(不做判断) → LPS调ags保存协议；无协议不落库')
