# 渠道中文名称 → partner_code 映射表

> 数据来源：`aps.partner_info` 表（STG1），查询时间 2026-07-01
> 用途：通过渠道中文名称/描述查找对应的 partner_code，禁止猜测

## 映射关系

| partner_code | 渠道中文名称 | 业务状态 |
|-------------|-------------|---------|
| TouTiao | 头条智选平台 | ONLINE |
| XingXuan | 头条星选 | OFFLINE |
| XCtrip | 新携程金融 | ONLINE |
| Ctrip | 携程 | OFFLINE |
| HuanBei | 新还呗 | ONLINE |
| DeWu | 得物API | ONLINE |
| DeWuCash | 得物现金贷API | ONLINE |
| DeWuXjd | 得物现金贷 | ONLINE |
| HuaWei | 华为 | ONLINE |
| EleMe | 饿了么 | ONLINE |
| EleMeB | 饿了么B | ONLINE |
| XEleMe | 新饿了么 | ONLINE |
| XEleMeB | 新饿了么B | ONLINE |
| DianXin | 电信翼支付 | ONLINE |
| TianCheng | 电信甜橙 | ONLINE |
| JdJieQian | 京东借钱 | ONLINE |
| JdJinTiao | 京东金条 | ONLINE |
| JdJiJian | 京东预借款二合一 | ONLINE |
| JdXiaoWei | 京东小微 | ONLINE |
| LianTong | 联通沃易贷 | ONLINE |
| XDiDi | 滴滴2.0 | ONLINE |
| DiDi | 滴滴 | OFFLINE |
| XMeiTuan | 新美团 | ONLINE |
| MeiTuan | 美团网 | OFFLINE |
| BaiDu | 度小满 | OFFLINE |
| XKuaiShou | 快手 | ONLINE |
| HaiEr | 海尔消金 | ONLINE |
| BaiXin | 云闪付百信 | ONLINE |
| BaiXinXx | 百信星选 | ONLINE |
| HuaRun | 华润银行 | ONLINE |
| ZhongYouGT | 中邮广投API | ONLINE |
| ZhongYouPt | 中邮平台 | ONLINE |
| ZhongYouHB | 中邮荷包 | ONLINE |
| ZhongBang | 众邦银行 | ONLINE |
| XianYu | 闲鱼渠道 | ONLINE |
| TongCheng | 同程 | ONLINE |
| NingBoBk | 宁波银行 | ONLINE |
| NingYinXJ | 宁银消金 | ONLINE |
| NingYinJLRD | 宁银消金拒量融担 | ONLINE |
| GuangDa | 光大渠道 | ONLINE |
| YiXinYxh | 宜信-宜享花 | ONLINE |
| Fumin | 富民 | ONLINE |
| JinCheng | 金城银行 | ONLINE |
| JinKe | 金科-吉林银行 | ONLINE |
| Shrcb | 上海农商行 | ONLINE |
| WeiLiDaiDL | 微粒贷 | ONLINE |
| WeiLiDaiXingYe | 微粒贷兴业 | ONLINE |
| XiaoEDL | 小鹅花钱 | ONLINE |
| JiangSuBk | 江苏银行 | ONLINE |
| HuaXing | 华兴银行 | ONLINE |
| GuaZi | 瓜子二手车 | ONLINE |
| PingAnPh | 平安普惠 | ONLINE |
| ZhaoLianJR | 招联金融 | ONLINE |
| ZhaoLianJiJian | 招联金融2.0 | ONLINE |
| RongYao | 荣耀 | ONLINE |
| GaoDe | 高德渠道 | ONLINE |
| SuShangBK | 苏商银行 | ONLINE |
| BoHaiXiaoWei | 渤海小微 | ONLINE |
| BoHaiBk | 渤海星选 | ONLINE |
| FxjPingAn | 放心借-平安 | ONLINE |
| Sykcfc | 苏银凯基 | ONLINE |
| Vips | 唯品会 | ONLINE |
| XiaoMiTX | 小米天星 | ONLINE |
| TaoBao | 淘宝借钱 | ONLINE |
| Gome | 美易借钱 | ONLINE |
| Jiayin | 极融借款 | ONLINE |
| MaYiBaiXin | 蚂蚁百信 | ONLINE |
| MaYiDc | 蚂蚁贷超 | ONLINE |
| SuNingXD | 苏宁小贷 | ONLINE |
| SSDMaYi | 随身贷蚂蚁 | ONLINE |
| SSDBaiXin | 随身贷百信 | ONLINE |
| WSGuangYinRD | 网商广银 | ONLINE |
| WSBaiXin | 网商百信 | ONLINE |
| WSJiangSuRD | 网商江苏 | ONLINE |
| XingHeBaiXin | 星河百信API | ONLINE |
| ZhongYinXJJLRD | 中银消金 | ONLINE |
| YouQianHua | 百度有钱花 | ONLINE |
| WeiBoJq | 微博借钱API | OFFLINE |
| ... | ... | ... |

> 完整数据保留在 `memory/api_channels_rules/partner_code_mapping.json`
