# 完整标准条文数据
# 用于初始化数据库

STANDARD_CLAUSES = [
    # ========== Q1 控制项 ==========
    {"clause_number": "5.1.1.1", "chapter": "control", "clause_type": "control", 
     "description": "场地主要人行出入口与周边人行道应无障碍衔接，形成连贯的无障碍通行流线", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "Q1", "max_score": 0},
    
    {"clause_number": "5.1.1.2", "chapter": "control", "clause_type": "control", 
     "description": "居住区道路、绿地和活动场地的无障碍设施应符合规定", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "Q1", "max_score": 0},
    
    {"clause_number": "5.1.1.3", "chapter": "control", "clause_type": "control", 
     "description": "无障碍机动车停车位的设置及数量应符合规定", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "Q1", "max_score": 0},
    
    {"clause_number": "5.1.1.4", "chapter": "control", "clause_type": "control", 
     "description": "无障碍电梯设置应符合规定（居住建筑/公共建筑分别要求）", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "Q1", "max_score": 0},
    
    {"clause_number": "5.1.1.5", "chapter": "control", "clause_type": "control", 
     "description": "无障碍通行设施应符合表4规定（通道、坡道、出入口、门、电梯、楼梯、扶手、停车位、缘石坡道、盲道等）", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "Q1", "max_score": 0},
    
    # ========== Q2 控制项 ==========
    {"clause_number": "6.1.1.1", "chapter": "control", "clause_type": "control", 
     "description": "通往公共无障碍服务设施的通道应为无障碍通道", 
     "score_type": "boolean", "applicable": ["non_residential", "public_with_accom", "public_no_accom"],
     "parent": "Q2", "max_score": 0},
    
    {"clause_number": "6.1.1.2", "chapter": "control", "clause_type": "control", 
     "description": "公共卫生间（厕所）的无障碍配置应符合规定", 
     "score_type": "boolean", "applicable": ["non_residential", "public_with_accom", "public_no_accom"],
     "parent": "Q2", "max_score": 0},
    
    {"clause_number": "6.1.1.3", "chapter": "control", "clause_type": "control", 
     "description": "轮椅席位的位置应符合规定", 
     "score_type": "boolean", "applicable": ["non_residential", "public_with_accom", "public_no_accom"],
     "parent": "Q2", "max_score": 0},
    
    {"clause_number": "6.1.1.4", "chapter": "control", "clause_type": "control", 
     "description": "低位服务设施的配置应符合规定", 
     "score_type": "boolean", "applicable": ["non_residential", "public_with_accom", "public_no_accom"],
     "parent": "Q2", "max_score": 0},
    
    {"clause_number": "6.1.1.5", "chapter": "control", "clause_type": "control", 
     "description": "公共无障碍服务设施应符合表15规定（坐便器、小便器、洗手盆、淋浴间、盆浴间、卫生间、浴室、轮椅席位、低位服务设施）", 
     "score_type": "boolean", "applicable": ["non_residential", "public_with_accom", "public_no_accom"],
     "parent": "Q2", "max_score": 0},
    
    # ========== Q3 控制项 ==========
    {"clause_number": "7.1.1.1", "chapter": "control", "clause_type": "control", 
     "description": "无障碍客房和无障碍住房、居室应符合规定", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom"],
     "parent": "Q3", "max_score": 0},
    
    {"clause_number": "7.1.1.2", "chapter": "control", "clause_type": "control", 
     "description": "住宅公共部分如有公共无障碍服务设施时应符合规定", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom"],
     "parent": "Q3", "max_score": 0},
    
    {"clause_number": "7.1.1.3", "chapter": "control", "clause_type": "control", 
     "description": "窗户可开启扇的执手或启闭开关应符合规定", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom"],
     "parent": "Q3", "max_score": 0},
    
    {"clause_number": "7.1.1.4", "chapter": "control", "clause_type": "control", 
     "description": "家具、部件的具体要求（开关面板、门禁、床侧通道）", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom"],
     "parent": "Q3", "max_score": 0},
    
    {"clause_number": "7.1.1.5", "chapter": "control", "clause_type": "control", 
     "description": "无障碍厨房应符合规定，灶具采用电灶具或配备安全装置", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom"],
     "parent": "Q3", "max_score": 0},
    
    {"clause_number": "7.1.1.6", "chapter": "control", "clause_type": "control", 
     "description": "宿舍/旅馆建筑的无障碍设施应符合规定", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom"],
     "parent": "Q3", "max_score": 0},
    
    # ========== Q4 控制项 ==========
    {"clause_number": "8.1.1.1", "chapter": "control", "clause_type": "control", 
     "description": "无障碍标识的设置应符合规定", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "Q4", "max_score": 0},
    
    {"clause_number": "8.1.1.2", "chapter": "control", "clause_type": "control", 
     "description": "公共场所和公共服务的无障碍信息交流应符合规定", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "Q4", "max_score": 0},
    
    {"clause_number": "8.1.1.3", "chapter": "control", "clause_type": "control", 
     "description": "公共场所中的网络通信设备部件应符合规定", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "Q4", "max_score": 0},
    
    # ========== 施工验收控制项（9章，仅竣工一年内项目参评） ==========
    {"clause_number": "9.1.1.1", "chapter": "control", "clause_type": "control",
     "description": "无障碍设施施工验收中设计、施工、监理单位的各方职责应符合GB50642中3.1.1~3.1.7条规定",
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "construction", "max_score": 0},

    {"clause_number": "9.1.1.2", "chapter": "control", "clause_type": "control",
     "description": "无障碍设施验收应符合GB50642中相应规定",
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "construction", "max_score": 0},

    {"clause_number": "9.1.1.3", "chapter": "control", "clause_type": "control",
     "description": "应对无障碍设施地面防滑性能、扶手和安全抓杆受力性能、安全抓杆预埋件进行验收并形成验收文件",
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "construction", "max_score": 0},

    # ========== 运行维护控制项（10章） ==========
    {"clause_number": "10.1.1.1", "chapter": "control", "clause_type": "control",
     "description": "建立通用管理制度（管理维护目标/监督检查维护制度/意见调查分析制度）",
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "maintenance", "max_score": 0},

    {"clause_number": "10.1.1.2", "chapter": "control", "clause_type": "control",
     "description": "无障碍设施竣工验收后应按GB50642明确无障碍设施维护人",
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "maintenance", "max_score": 0},

    {"clause_number": "10.1.1.3", "chapter": "control", "clause_type": "control",
     "description": "投入使用后应按GB50642进行检查、每季度维护监督、每年岗位技能审查并记录",
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "maintenance", "max_score": 0},

    {"clause_number": "10.1.1.4", "chapter": "control", "clause_type": "control",
     "description": "无障碍设施的维护应符合GB50642中4.4节的规定",
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "maintenance", "max_score": 0},

    # ========== Q1 系统评分项 S1（满分100分） ==========
    # 5.2.1 建筑场地（40分）
    {"clause_number": "5.2.1.1", "chapter": "Q1", "clause_type": "system", 
     "description": "场地主要人行出入口与周边人行道的无障碍衔接方式（平坡8分/台阶+坡道6分/4分）", 
     "score_type": "single_choice", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "options": [{"label": "地面采用坡度不大于1:20的平坡", "score": 8}, {"label": "同时设有台阶和轮椅坡道，坡度不大于1:14", "score": 6}, {"label": "同时设有台阶和轮椅坡道，坡度不大于1:12", "score": 4}], "parent": "5.2.1", "max_score": 8, "sort_order": 1},
    
    {"clause_number": "5.2.1.2", "chapter": "Q1", "clause_type": "system", 
     "description": "无障碍通行流线与主要人行流线路径的一致性（一致8分/不一致但无绕行6分/有绕行≤30% 4分）", 
     "score_type": "single_choice", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "options": [{"label": "无障碍通行流线与主要人行流线路径一致", "score": 8}, {"label": "不一致，但不存在绕行", "score": 6}, {"label": "不一致，因合理原因绕行不超过30%", "score": 4}], "parent": "5.2.1", "max_score": 8, "sort_order": 2},
    
    {"clause_number": "5.2.1.3", "chapter": "Q1", "clause_type": "system", 
     "description": "大型公共建筑场地人车分流情况（全部分流6分/出入口分流4分/混流限速2分）", 
     "score_type": "single_choice", "applicable": ["public_with_accom", "public_no_accom"],
     "options": [{"label": "全部主要人行流线人车分流", "score": 6}, {"label": "场地出入口到建筑无障碍入口人车分流", "score": 4}, {"label": "人车混流，场地内机动车限速20公里", "score": 2}], "parent": "5.2.1", "max_score": 6, "sort_order": 3},
    
    {"clause_number": "5.2.1.4", "chapter": "Q1", "clause_type": "system", 
     "description": "视觉障碍者集中使用建筑设连贯盲道路径", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "5.2.1", "max_score": 4, "sort_order": 4},
    
    {"clause_number": "5.2.1.5", "chapter": "Q1", "clause_type": "system", 
     "description": "设有2个及以上无障碍出入口、无障碍游览流线等（共8分）", 
     "score_type": "calculated", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "5.2.1", "max_score": 8, "sort_order": 5},
    
    {"clause_number": "5.2.1.6", "chapter": "Q1", "clause_type": "system", 
     "description": "场地主要无障碍通行流线设休息座椅、遮雨措施、夜间照明（共6分）", 
     "score_type": "calculated", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "5.2.1", "max_score": 6, "sort_order": 6},
    
    # 5.2.2 停车（20分）
    {"clause_number": "5.2.2.1", "chapter": "Q1", "clause_type": "system", 
     "description": "无障碍机动车停车位设置比例（<50辆≥1个:12分/<100辆≥1个:8分）", 
     "score_type": "single_choice", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "options": [{"label": "50辆以下≥1个/100辆以下≥2个/100辆以上≥2%", "score": 12}, {"label": "100辆以下≥1个/100辆以上≥1%", "score": 8}], "parent": "5.2.2", "max_score": 12, "sort_order": 1},
    
    {"clause_number": "5.2.2.2", "chapter": "Q1", "clause_type": "system", 
     "description": "停车场入口及内部设有连续导向标识", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "5.2.2", "max_score": 3, "sort_order": 2},
    
    {"clause_number": "5.2.2.3", "chapter": "Q1", "clause_type": "system", 
     "description": "配置充电桩的停车场至少1个无障碍车位安装充电桩", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "5.2.2", "max_score": 2, "sort_order": 3},
    
    {"clause_number": "5.2.2.4", "chapter": "Q1", "clause_type": "system", 
     "description": "提供公共服务的建筑设置残疾人代步车专用车位", 
     "score_type": "boolean", "applicable": ["public_with_accom", "public_no_accom"],
     "parent": "5.2.2", "max_score": 2, "sort_order": 4},
    
    {"clause_number": "5.2.2.5", "chapter": "Q1", "clause_type": "system", 
     "description": "地上停车位按不小于无障碍车位比例设置地上无障碍车位", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "5.2.2", "max_score": 1, "sort_order": 5},
    
    # 5.2.3 出入口及内部交通（40分）
    {"clause_number": "5.2.3.1", "chapter": "Q1", "clause_type": "system", 
     "description": "建筑无障碍出入口设置比例（所有出入口:8分/主要出入口:6分/主出入口受限:4分）", 
     "score_type": "single_choice", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "options": [{"label": "所有建筑出入口均为无障碍出入口", "score": 8}, {"label": "建筑主要出入口为无障碍出入口", "score": 6}, {"label": "主出入口受地形限制，设有其他无障碍出入口并有明确引导标识", "score": 4}], "parent": "5.2.3", "max_score": 8, "sort_order": 1},
    
    {"clause_number": "5.2.3.2", "chapter": "Q1", "clause_type": "system",
     "description": "公共建筑无障碍电梯配置及功能（每组客梯含无障碍电梯4分/连通主要空间4分/单独控制2分）",
     "score_type": "calculated", "applicable": ["public_with_accom", "public_no_accom"],
     "parent": "5.2.3", "max_score": 10, "sort_order": 2},
    
    {"clause_number": "5.2.3.3", "chapter": "Q1", "clause_type": "system", 
     "description": "楼梯及台阶的无障碍功能（所有符合:4分/主要楼梯符合:2分）", 
     "score_type": "single_choice", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "options": [{"label": "内部不同功能区的主要楼梯及所有台阶均符合GB55019第2.7节", "score": 4}, {"label": "未设电梯的功能区的主要楼梯及主要台阶均符合", "score": 2}], "parent": "5.2.3", "max_score": 4, "sort_order": 3},
    
    {"clause_number": "5.2.3.4", "chapter": "Q1", "clause_type": "system", 
     "description": "无障碍通行流线上的高差处理（全程无高差:8分/坡度≤1:12:6分/4分）", 
     "score_type": "single_choice", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "options": [{"label": "全程无高差，或高差处设坡度≤1:14轮椅坡道（高差>300mm同时设台阶）", "score": 8}, {"label": "高差处设坡度≤1:12轮椅坡道（高差>300mm同时设台阶）", "score": 6}, {"label": "高差处设坡度≤1:12轮椅坡道", "score": 4}], "parent": "5.2.3", "max_score": 8, "sort_order": 4},
    
    {"clause_number": "5.2.3.5", "chapter": "Q1", "clause_type": "system", 
     "description": "走道扶手、阳角防护、护墙板、防撞提示（共4分）", 
     "score_type": "calculated", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "5.2.3", "max_score": 4, "sort_order": 5},
    
    {"clause_number": "5.2.3.6", "chapter": "Q1", "clause_type": "system", 
     "description": "无障碍通行流线上门的设置（主要自动门+其他:6分/非弹簧门:4分）", 
     "score_type": "single_choice", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "options": [{"label": "主要通道及高频公共功能空间的门采用自动门，其他位置采用自动门/非弹簧门/非全玻璃平开门", "score": 6}, {"label": "均采用非弹簧门及非全玻璃门的平开门", "score": 4}], "parent": "5.2.3", "max_score": 6, "sort_order": 6},
    
    # ========== Q4 系统评分项（满分100分） ==========
    # 8.2.1 无障碍标识（60分）
    {"clause_number": "8.2.1.1", "chapter": "Q4", "clause_type": "system", 
     "description": "标识正确使用GB/T10001.9符号或国际通用符号", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "8.2.1", "max_score": 10, "sort_order": 1},
    
    {"clause_number": "8.2.1.2", "chapter": "Q4", "clause_type": "system", 
     "description": "标识符合GB/T20501.1和GB/T20501.2规定", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "8.2.1", "max_score": 10, "sort_order": 2},
    
    {"clause_number": "8.2.1.3", "chapter": "Q4", "clause_type": "system", 
     "description": "系统设置无障碍标识，出具专篇说明并实施", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "8.2.1", "max_score": 10, "sort_order": 3},
    
    {"clause_number": "8.2.1.4", "chapter": "Q4", "clause_type": "system", 
     "description": "室内外视觉信息标识在正常视距范围内保证80%以上有出行需要的人获得必要信息", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "8.2.1", "max_score": 10, "sort_order": 4},
    
    {"clause_number": "8.2.1.5", "chapter": "Q4", "clause_type": "system", 
     "description": "无障碍流线上设有完整连续的无障碍设施导向标识", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "8.2.1", "max_score": 10, "sort_order": 5},
    
    {"clause_number": "8.2.1.6", "chapter": "Q4", "clause_type": "system", 
     "description": "无障碍标志设置夜间照明或内置光源", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "8.2.1", "max_score": 5, "sort_order": 6},
    
    {"clause_number": "8.2.1.7", "chapter": "Q4", "clause_type": "system", 
     "description": "二条以上人行流线时，设置标识标明无障碍通道", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "8.2.1", "max_score": 5, "sort_order": 7},
    
    # 8.2.2 信息（20分）
    {"clause_number": "8.2.2.1", "chapter": "Q4", "clause_type": "system", 
     "description": "安全应急信息同时提供视觉和听觉（或触觉）信息", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "8.2.2", "max_score": 5, "sort_order": 1},
    
    {"clause_number": "8.2.2.2", "chapter": "Q4", "clause_type": "system", 
     "description": "无障碍住宿门铃设置闪光声音功能", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom"],
     "parent": "8.2.2", "max_score": 4, "sort_order": 2},
    
    {"clause_number": "8.2.2.3", "chapter": "Q4", "clause_type": "system", 
     "description": "无障碍客房、宿舍及视觉障碍者房间内贴有对比度明显的安全疏散线路信息", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom"],
     "parent": "8.2.2", "max_score": 5, "sort_order": 3},
    
    {"clause_number": "8.2.2.4", "chapter": "Q4", "clause_type": "system", 
     "description": "出入口设建筑平面总览图，配置大字体文字和盲文标识", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "8.2.2", "max_score": 4, "sort_order": 4},
    
    {"clause_number": "8.2.2.5", "chapter": "Q4", "clause_type": "system", 
     "description": "盲文辅助信息触摸表面光滑无刺", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "8.2.2", "max_score": 2, "sort_order": 5},
    
    # 8.2.3 无障碍智慧服务（20分）
    {"clause_number": "8.2.3.1", "chapter": "Q4", "clause_type": "system", 
     "description": "门禁设置中心距地0.85m~1.00m的低位刷卡或刷脸处", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "8.2.3", "max_score": 5, "sort_order": 1},
    
    {"clause_number": "8.2.3.2", "chapter": "Q4", "clause_type": "system", 
     "description": "门禁前地面设置长度≥500mm提示盲道", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "8.2.3", "max_score": 5, "sort_order": 2},
    
    {"clause_number": "8.2.3.3", "chapter": "Q4", "clause_type": "system", 
     "description": "智能灯具、操控面板等易于不同障碍类别人员识别和使用", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "8.2.3", "max_score": 5, "sort_order": 3},
    
    {"clause_number": "8.2.3.4", "chapter": "Q4", "clause_type": "system", 
     "description": "操作面板、电话、闹钟等设有大字号、高对比度显示屏", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "8.2.3", "max_score": 5, "sort_order": 4},
    
    # ========== 施工验收（满分100分） ==========
    {"clause_number": "9.2.1.1", "chapter": "construction", "clause_type": "system", 
     "description": "设计单位就审查合格的施工图设计文件向施工单位进行技术交底时，对无障碍设施作出专项说明并形成会议纪要", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "9.2.1", "max_score": 20, "sort_order": 1},
    
    {"clause_number": "9.2.1.2", "chapter": "construction", "clause_type": "system", 
     "description": "施工单位编制无障碍设施专项施工方案，经技术负责人签字，报总监理工程师审核通过", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "9.2.1", "max_score": 20, "sort_order": 2},
    
    {"clause_number": "9.2.1.3", "chapter": "construction", "clause_type": "system", 
     "description": "项目监理部编制的监理实施细则包括无障碍设施相关内容", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "9.2.1", "max_score": 10, "sort_order": 3},
    
    {"clause_number": "9.2.1.4", "chapter": "construction", "clause_type": "system", 
     "description": "施工单位制定无障碍设施施工操作规程并在施工过程中实施", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "9.2.1", "max_score": 10, "sort_order": 4},
    
    {"clause_number": "9.2.1.5", "chapter": "construction", "clause_type": "system", 
     "description": "无障碍厕所、无障碍住宿及其他必要设施设置样板间，编制专项方案并审核通过", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "9.2.1", "max_score": 10, "sort_order": 5},
    
    {"clause_number": "9.2.1.6", "chapter": "construction", "clause_type": "system", 
     "description": "无障碍样板间设置时间（主体结构施工阶段:10分/二次结构施工前:5分）", 
     "score_type": "single_choice", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "options": [{"label": "主体结构施工阶段设置完成", "score": 10}, {"label": "二次结构施工前设置完成", "score": 5}], "parent": "9.2.1", "max_score": 10, "sort_order": 6},
    
    {"clause_number": "9.2.1.7", "chapter": "construction", "clause_type": "system", 
     "description": "建设单位组织样板间验收时邀请残疾人、老年人等代表试用体验并听取意见", 
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "9.2.1", "max_score": 20, "sort_order": 7},
    
    # ========== 运行维护（满分100分） ==========
    # 10.2.1 制度（30分）
    {"clause_number": "10.2.1.1", "chapter": "maintenance", "clause_type": "system",
     "description": "通用管理制度的有效性（持续改进3分/目标可行2分/制度明确2分/应急措施2分/违规处理2分/技能培训2分/意见反馈2分）",
     "score_type": "calculated", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "10.2.1", "max_score": 15, "sort_order": 1},

    {"clause_number": "10.2.1.2", "chapter": "maintenance", "clause_type": "system",
     "description": "无障碍设施维护制度的有效性（维护方案档案2分/技术交底2分/组织体系2分/考核指标3分/隐患排查3分/故障处理3分）",
     "score_type": "calculated", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "10.2.1", "max_score": 15, "sort_order": 2},

    # 10.2.2 运行维护（40分）
    {"clause_number": "10.2.2.1", "chapter": "maintenance", "clause_type": "system",
     "description": "无障碍设施维护（检查频次达标10分/加固修补性维护验收或检测20分）",
     "score_type": "calculated", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "10.2.2", "max_score": 30, "sort_order": 3},

    {"clause_number": "10.2.2.2", "chapter": "maintenance", "clause_type": "system",
     "description": "无障碍设施根据具体使用反馈当天检查，及时处理，避免安全隐患",
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "10.2.2", "max_score": 10, "sort_order": 4},

    # 10.2.3 绩效（30分）
    {"clause_number": "10.2.3.1", "chapter": "maintenance", "clause_type": "system",
     "description": "正常使用时段的无障碍设施完好率（≥90%:20分/≥80%:15分/≥70%:10分）",
     "score_type": "single_choice", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "options": [{"label": "无障碍设施完好率不低于90%", "score": 20}, {"label": "不低于80%", "score": 15}, {"label": "不低于70%", "score": 10}], "parent": "10.2.3", "max_score": 20, "sort_order": 5},

    {"clause_number": "10.2.3.2", "chapter": "maintenance", "clause_type": "system",
     "description": "使用者满意度不小于80%",
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "10.2.3", "max_score": 10, "sort_order": 6},

    # ========== Q2 公共无障碍服务系统评分项 S2（满分100分） ==========
    # 6.2.1 公共区（40分）
    {"clause_number": "6.2.1.1", "chapter": "Q2", "clause_type": "system",
     "description": "公共接待、休息区域与无障碍通行流线连接，在无障碍出入口处设有引导标识",
     "score_type": "boolean", "applicable": ["non_residential", "public_with_accom", "public_no_accom"],
     "parent": "6.2.1", "max_score": 5, "sort_order": 1},

    {"clause_number": "6.2.1.2", "chapter": "Q2", "clause_type": "system",
     "description": "服务接待处（低位无障碍服务台4分/信息获取4分/助听辅助系统2分/轮椅暂存租借3分）",
     "score_type": "calculated", "applicable": ["non_residential", "public_with_accom", "public_no_accom"],
     "parent": "6.2.1", "max_score": 13, "sort_order": 2},

    {"clause_number": "6.2.1.3", "chapter": "Q2", "clause_type": "system",
     "description": "靠近无障碍出入口处提供轮椅电动车头暂存空间及电动轮椅充电设施",
     "score_type": "boolean", "applicable": ["non_residential", "public_with_accom", "public_no_accom"],
     "parent": "6.2.1", "max_score": 3, "sort_order": 3},

    {"clause_number": "6.2.1.4", "chapter": "Q2", "clause_type": "system",
     "description": "休息区域（无障碍休息区4分/长走道休息区3分/服务犬休息空间3分）",
     "score_type": "calculated", "applicable": ["non_residential", "public_with_accom", "public_no_accom"],
     "parent": "6.2.1", "max_score": 10, "sort_order": 4},

    {"clause_number": "6.2.1.5", "chapter": "Q2", "clause_type": "system",
     "description": "固定观众席位时轮椅席位比例（按规模达标6分/降档3分）",
     "score_type": "single_choice", "applicable": ["non_residential", "public_with_accom", "public_no_accom"],
     "options": [{"label": "100座以下≥1个/101-300座≥2个/301-1000座≥3个/1000座以上≥0.3%", "score": 6}, {"label": "300座以下≥1个/301-1000座≥2个/1000座以上≥0.2%", "score": 3}], "parent": "6.2.1", "max_score": 6, "sort_order": 5},

    {"clause_number": "6.2.1.6", "chapter": "Q2", "clause_type": "system",
     "description": "轮椅席位的前或后为不小于1.2m的无障碍通道",
     "score_type": "boolean", "applicable": ["non_residential", "public_with_accom", "public_no_accom"],
     "parent": "6.2.1", "max_score": 3, "sort_order": 6},

    # 6.2.2 卫生设施（60分）
    {"clause_number": "6.2.2.1", "chapter": "Q2", "clause_type": "system",
     "description": "男女公共卫生间和无障碍厕所配置（每组附近均设20分/每层至少1个15分/首层或主要楼层10分）",
     "score_type": "single_choice", "applicable": ["non_residential", "public_with_accom", "public_no_accom"],
     "options": [{"label": "每组男、女公共卫生间附近均设有1个独立无障碍厕所", "score": 20}, {"label": "符合GB55019-3.2.4且每层同时设至少1个独立无障碍厕所", "score": 15}, {"label": "符合GB55019-3.2.4且大型/面向公众公共建筑在首层或主要楼层设至少1个", "score": 10}], "parent": "6.2.2", "max_score": 20, "sort_order": 7},

    {"clause_number": "6.2.2.2", "chapter": "Q2", "clause_type": "system",
     "description": "公共卫生间、无障碍厕所位置（靠近出入口8分/服务半径8分/距主流线≤20m 8分/引导标识8分）",
     "score_type": "calculated", "applicable": ["non_residential", "public_with_accom", "public_no_accom"],
     "parent": "6.2.2", "max_score": 32, "sort_order": 8},

    {"clause_number": "6.2.2.3", "chapter": "Q2", "clause_type": "system",
     "description": "独立母婴室（位置及无障碍通道4分/隐私独立出入口4分）",
     "score_type": "calculated", "applicable": ["non_residential", "public_with_accom", "public_no_accom"],
     "parent": "6.2.2", "max_score": 8, "sort_order": 9},

    # ========== Q3 无障碍住宿系统评分项 S3（满分100分） ==========
    {"clause_number": "7.2.1.1", "chapter": "Q3", "clause_type": "system",
     "description": "无障碍住宿配置比例（住宅预留条件40分/宿舍、旅馆符合配置20分+每增10%加5分，最高40分）",
     "score_type": "calculated", "applicable": ["residential", "non_residential", "public_with_accom"],
     "parent": "7.2.1", "max_score": 40, "sort_order": 1},

    {"clause_number": "7.2.1.2", "chapter": "Q3", "clause_type": "system",
     "description": "无障碍住宿的设置（底层靠近无障碍出入口30分/二层以上邻近无障碍电梯20分）",
     "score_type": "single_choice", "applicable": ["residential", "non_residential", "public_with_accom"],
     "options": [{"label": "至少1套设于底层并靠近无障碍出入口，其他设在二层及以上时邻近无障碍电梯", "score": 30}, {"label": "设在二层及以上时设置无障碍电梯并以无障碍通道连接", "score": 20}], "parent": "7.2.1", "max_score": 30, "sort_order": 2},

    {"clause_number": "7.2.1.3", "chapter": "Q3", "clause_type": "system",
     "description": "户内各功能空间之间通道均为宽度不小于1.2m的无障碍通道",
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom"],
     "parent": "7.2.1", "max_score": 10, "sort_order": 3},

    {"clause_number": "7.2.1.4", "chapter": "Q3", "clause_type": "system",
     "description": "户内主要人员活动空间设置救助呼叫装置，易于居住者识别和使用",
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom"],
     "parent": "7.2.1", "max_score": 10, "sort_order": 4},

    {"clause_number": "7.2.1.5", "chapter": "Q3", "clause_type": "system",
     "description": "家具安排不妨碍轮椅使用者使用窗户和窗帘，或设置遥控装置",
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom"],
     "parent": "7.2.1", "max_score": 5, "sort_order": 5},

    {"clause_number": "7.2.1.6", "chapter": "Q3", "clause_type": "system",
     "description": "户内各功能空间照明采用照度标准范围中的高标准",
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom"],
     "parent": "7.2.1", "max_score": 5, "sort_order": 6},

    # ========== Q5 创新与提升（上限20分） ==========
    {"clause_number": "11.1.1.1", "chapter": "Q5", "clause_type": "bonus",
     "description": "面向公众的公共建筑的公共通道两侧均设置符合要求的扶手",
     "score_type": "boolean", "applicable": ["public_with_accom", "public_no_accom"],
     "parent": "11.1.1", "max_score": 1, "sort_order": 1},

    {"clause_number": "11.1.1.2", "chapter": "Q5", "clause_type": "bonus",
     "description": "门扇无障碍提升（350mm护门板0.5分/关门侧横向执手0.5分）",
     "score_type": "calculated", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "11.1.1", "max_score": 1, "sort_order": 2},

    {"clause_number": "11.1.1.3", "chapter": "Q5", "clause_type": "bonus",
     "description": "无障碍电梯提升（脚动呼叫装置0.5分/轿厢侧壁低位操控面板0.5分）",
     "score_type": "calculated", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "11.1.1", "max_score": 1, "sort_order": 3},

    {"clause_number": "11.1.1.4", "chapter": "Q5", "clause_type": "bonus",
     "description": "大型公共建筑场地人行流线上设有连贯盲道路径连接主要出入口",
     "score_type": "boolean", "applicable": ["public_with_accom", "public_no_accom"],
     "parent": "11.1.1", "max_score": 1, "sort_order": 4},

    {"clause_number": "11.1.1.5", "chapter": "Q5", "clause_type": "bonus",
     "description": "所有人员使用的楼梯/台阶满足GB55019中2.7.1条要求",
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "11.1.1", "max_score": 1, "sort_order": 5},

    {"clause_number": "11.1.1.6", "chapter": "Q5", "clause_type": "bonus",
     "description": "50%的无障碍机动车停车位在两侧均设有轮椅通道",
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "11.1.1", "max_score": 1, "sort_order": 6},

    {"clause_number": "11.1.1.7", "chapter": "Q5", "clause_type": "bonus",
     "description": "公共卫生间无障碍提升（儿童便器0.5分/儿童座椅0.5分/手持喷头0.5分）",
     "score_type": "calculated", "applicable": ["non_residential", "public_with_accom", "public_no_accom"],
     "parent": "11.1.1", "max_score": 1.5, "sort_order": 7},

    {"clause_number": "11.1.1.8", "chapter": "Q5", "clause_type": "bonus",
     "description": "无障碍厕所提升（自动推拉门1分/U形抓杆0.5分/靠背0.5分/清洗盆0.5分）",
     "score_type": "calculated", "applicable": ["non_residential", "public_with_accom", "public_no_accom"],
     "parent": "11.1.1", "max_score": 2.5, "sort_order": 8},

    {"clause_number": "11.1.1.9", "chapter": "Q5", "clause_type": "bonus",
     "description": "公共建筑首层或主要楼层设置面积不小于6.50㎡的家庭卫生间",
     "score_type": "boolean", "applicable": ["public_with_accom", "public_no_accom"],
     "parent": "11.1.1", "max_score": 1, "sort_order": 9},

    {"clause_number": "11.1.1.10", "chapter": "Q5", "clause_type": "bonus",
     "description": "住宅无障碍住房总套数在配置要求基础上每增加10%得1分，最高3分",
     "score_type": "calculated", "applicable": ["residential"],
     "parent": "11.1.1", "max_score": 3, "sort_order": 10},

    {"clause_number": "11.1.1.11", "chapter": "Q5", "clause_type": "bonus",
     "description": "无障碍标识包含关键信息并同时提供触觉或听觉信息",
     "score_type": "boolean", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "11.1.1", "max_score": 1, "sort_order": 11},

    {"clause_number": "11.1.1.12", "chapter": "Q5", "clause_type": "bonus",
     "description": "大型公共建筑智能化管理平台包含无障碍服务内容（设施查询0.5/导航模式0.5/信息同步0.5/紧急呼叫0.5）",
     "score_type": "calculated", "applicable": ["public_with_accom", "public_no_accom"],
     "parent": "11.1.1", "max_score": 2, "sort_order": 12},

    {"clause_number": "11.1.1.13", "chapter": "Q5", "clause_type": "bonus",
     "description": "增设本文件之外的新技术或产品并有效帮助有无障碍需要人士，每项1分，最高3分",
     "score_type": "calculated", "applicable": ["residential", "non_residential", "public_with_accom", "public_no_accom"],
     "parent": "11.1.1", "max_score": 3, "sort_order": 13},
]

# 设施评分项模板
FACILITY_CLAUSES = {
    "通道": [
        {"clause_number": "5.3.1.1a", "max_score": 1, "description": "通道地板、墙面有颜色差异"},
        {"clause_number": "5.3.1.1b", "max_score": 1, "description": "通道采光或照度均匀，地面照度≥100lx"},
        {"clause_number": "5.3.1.1c", "max_score": 1, "description": "通道地面未使用地毯，或使用绒毛高度<9mm地毯并固定"},
        {"clause_number": "5.3.1.1d", "max_score": 1, "description": "通道地面未采用易引起视觉错觉的图案"},
        {"clause_number": "5.3.1.2a", "max_score": 1, "description": "未设置井盖/箅子，或有足够宽度通行不经过"},
        {"clause_number": "5.3.1.2b", "max_score": 1, "description": "自动扶梯、楼梯梯段下部不作为人行主要通道"},
        {"clause_number": "5.3.1.2c", "max_score": 2, "description": "靠近人体头部的安全阻挡设施采取避免磕碰的防护措施"},
        {"clause_number": "5.3.1.3", "max_score": 2, "description": "通道通行净宽≥1.50m，或设有轮椅避让空间"},
    ],
    "坡道": [
        {"clause_number": "5.3.2.1", "max_score": 1, "description": "轮椅坡道设计成直线形、直角形或折返形，未采用曲线形"},
        {"clause_number": "5.3.2.2", "max_score": 2, "description": "轮椅坡道上下坡处未设置井盖和篦子"},
        {"clause_number": "5.3.2.3", "max_score": 1, "description": "轮椅坡道坡面或外缘与相邻墙壁和地面颜色有明显差异"},
        {"clause_number": "5.3.2.4", "max_score": 1, "description": "无障碍出入口处的室外轮椅坡道设有遮雨措施"},
        {"clause_number": "5.3.2.5", "max_score": 1, "description": "大于1:20的轮椅坡道临空侧设有安全阻挡措施"},
        {"clause_number": "5.3.2.6", "max_score": 2, "description": "提升高度>100mm且坡度>1:20时，至少于一侧设有扶手"},
        {"clause_number": "5.3.2.7", "max_score": 2, "description": "休息平台连接坡道宽度变化时，平台宽度不小于较宽坡道宽度"},
    ],
    "出入口": [
        {"clause_number": "5.3.3.1", "max_score": 3, "description": "主要无障碍出入口形式（平坡3分/台阶+坡道2分/1分）",
         "options": [{"label": "平坡出入口", "score": 3}, {"label": "同时设置台阶和轮椅坡道，坡度不大于1:14、宽度不小于1.2m", "score": 2}, {"label": "同时设置台阶和轮椅坡道，坡度不大于1:12、宽度不小于1.2m", "score": 1}]},
        {"clause_number": "5.3.3.2a", "max_score": 1, "description": "无障碍流线上转折/分岔处均设有指向无障碍出入口的标识"},
        {"clause_number": "5.3.3.2b", "max_score": 1, "description": "无障碍出入口的门采用符合要求的自动门"},
        {"clause_number": "5.3.3.2c", "max_score": 1, "description": "出入口地面平整防滑，铺地材料固定无卷边"},
        {"clause_number": "5.3.3.2d", "max_score": 1, "description": "建筑出入口上方雨篷挑出长度≥1.50m"},
        {"clause_number": "5.3.3.3", "max_score": 1, "description": "无障碍出入口前设有无障碍小汽（客）车上客落客区"},
        {"clause_number": "5.3.3.4", "max_score": 1, "description": "无障碍出入口设有车档时，车档净间距≥900mm"},
        {"clause_number": "5.3.3.5", "max_score": 1, "description": "手动操作装置中心距地0.85m~1.00m，前设长度≥500mm提示盲道"},
    ],
    "门": [
        {"clause_number": "5.3.4.1a", "max_score": 2, "description": "门扇内外空间及门执手一侧墙面宽度符合规定"},
        {"clause_number": "5.3.4.1b", "max_score": 1, "description": "门扇与周围墙面具有色彩或亮度差异，或设置明显标识"},
        {"clause_number": "5.3.4.1c", "max_score": 1, "description": "手动双扇门其中一扇开启后通行净宽≥900mm"},
        {"clause_number": "5.3.4.1d", "max_score": 1, "description": "平开门、推拉门、折叠门设有视线观察玻璃"},
        {"clause_number": "5.3.4.2a", "max_score": 0.5, "description": "自动门内外无高差和门槛"},
        {"clause_number": "5.3.4.2b", "max_score": 0.5, "description": "手动启闭装置与背景有亮度/颜色差异"},
        {"clause_number": "5.3.4.2c", "max_score": 0.5, "description": "手动启闭装置前设有长度≥500mm提示盲道"},
        {"clause_number": "5.3.4.2d", "max_score": 0.5, "description": "用≤25N力度可让门停止运动"},
        {"clause_number": "5.3.4.3a", "max_score": 1, "description": "手动推拉门/平开门内外无高差和门槛"},
        {"clause_number": "5.3.4.3b", "max_score": 1, "description": "推拉门执手外露杆状，门内外均设执手；平开门内外均设执手"},
        {"clause_number": "5.3.4.3c", "max_score": 0.5, "description": "门执手与门饰面有亮度或颜色差异"},
        {"clause_number": "5.3.4.3d", "max_score": 0.5, "description": "闭门器从最大受控角度到关闭前10°时间≥5秒"},
    ],
    "电梯": [
        {"clause_number": "5.3.5.1a", "max_score": 1, "description": "轿厢内除正面外采用无反光哑光饰面"},
        {"clause_number": "5.3.5.1b", "max_score": 1, "description": "轿厢内照度与走廊相同无闪烁，≥100lx"},
        {"clause_number": "5.3.5.1c", "max_score": 1, "description": "轿厢内未采用深色地板"},
        {"clause_number": "5.3.5.2", "max_score": 3, "description": "无障碍电梯轿厢尺寸（≥2.10m×1.50m:3分/≥1.50m×1.60m:2分）",
         "options": [{"label": "每个主要功能分区/单元有一部轿厢不小于2.10m×1.50m", "score": 3}, {"label": "有一部轿厢不小于1.50m×1.60m 或 2.10m(深)×1.10m(宽)", "score": 2}]},
        {"clause_number": "5.3.5.3a", "max_score": 1, "description": "无障碍电梯门与毗邻墙面有亮度或颜色差异"},
        {"clause_number": "5.3.5.3b", "max_score": 1, "description": "室外无障碍电梯设有深度≥1.2m的雨篷"},
        {"clause_number": "5.3.5.4a", "max_score": 1, "description": "电梯厅呼叫按钮前提示盲道长度≥500mm"},
        {"clause_number": "5.3.5.4b", "max_score": 1, "description": "按钮设置盲文时，盲文在按钮侧而非按钮上"},
    ],
    "盲道": [
        {"clause_number": "5.3.6.1", "max_score": 3, "description": "行进盲道设置与人行道走向一致，避免连续<135°折线"},
        {"clause_number": "5.3.6.2a", "max_score": 1, "description": "盲道上空没有低于2.00m的障碍物"},
        {"clause_number": "5.3.6.2b", "max_score": 1, "description": "非机动车停放位置不侵占盲道"},
        {"clause_number": "5.3.6.2c", "max_score": 1, "description": "提示盲道长度≥500mm，与警示范围相对应"},
        {"clause_number": "5.3.6.2d", "max_score": 1, "description": "行进盲道宽度250mm~400mm"},
        {"clause_number": "5.3.6.2e", "max_score": 0.5, "description": "行进盲道距围墙/花台/绿化带250mm~600mm"},
        {"clause_number": "5.3.6.2f", "max_score": 0.5, "description": "行进盲道<135°转弯处设有提示盲道"},
        {"clause_number": "5.3.6.2g", "max_score": 1, "description": "盲道无破损"},
        {"clause_number": "5.3.6.3", "max_score": 1, "description": "盲道采用中黄色"},
    ],
    "其他通行设施": [
        {"clause_number": "5.3.7.1a", "max_score": 1, "description": "主要使用楼梯和台阶两侧均设有扶手"},
        {"clause_number": "5.3.7.1b", "max_score": 1, "description": "室外楼梯和台阶采取遮雨措施"},
        {"clause_number": "5.3.7.1c", "max_score": 1, "description": "楼梯栏杆下方设有安全阻挡措施"},
        {"clause_number": "5.3.7.1d", "max_score": 1, "description": "楼梯扶手起止处设有可触摸数字指示楼层"},
        {"clause_number": "5.3.7.2", "max_score": 1, "description": "无障碍设施处通过盲文或其他可触摸标记提供设施信息"},
        {"clause_number": "5.3.7.3", "max_score": 2, "description": "室外扶手不采用不锈钢等不防滑、热惰性差的金属材料"},
        {"clause_number": "5.3.7.4", "max_score": 1, "description": "室外无障碍机动车停车位轮椅通道上方设有遮雨措施"},
        {"clause_number": "5.3.7.5", "max_score": 1, "description": "采用坡度<1:20全宽式单面坡缘石坡道，或坡度<1:14三面坡缘石坡道"},
        {"clause_number": "5.3.7.6", "max_score": 1, "description": "缘石坡道不侵占非机动车道和机动车道"},
    ],
    "公共卫生间": [
        {"clause_number": "6.3.1.1a", "max_score": 3, "description": "女卫生间设婴儿打理台和低位洗手台；男卫生间设低位洗手台"},
        {"clause_number": "6.3.1.1b", "max_score": 1, "description": "设长度≥700mm、宽度≥400mm、高度550~650mm的多功能台"},
        {"clause_number": "6.3.1.1c", "max_score": 1, "description": "设紧急情况声光报警灯"},
        {"clause_number": "6.3.1.2a", "max_score": 0.5, "description": "设距离地面1.10m~1.20m的低位挂衣钩"},
        {"clause_number": "6.3.1.2b", "max_score": 0.5, "description": "坐便器冲水装置为感应式自动冲水"},
        {"clause_number": "6.3.1.2c", "max_score": 0.5, "description": "取纸器竖向中心线位于坐便器前端≤250mm处"},
        {"clause_number": "6.3.1.2d", "max_score": 0.5, "description": "设坐姿和倒地高度两处紧急呼叫按钮或拉绳"},
        {"clause_number": "6.3.1.3a", "max_score": 1, "description": "洗手盆设有便于使用的安全抓杆"},
        {"clause_number": "6.3.1.3b", "max_score": 0.5, "description": "洗手盆一侧配有置物台"},
        {"clause_number": "6.3.1.3c", "max_score": 0.5, "description": "供水排水管道绝热或配备防接触设施"},
        {"clause_number": "6.3.1.4", "max_score": 1, "description": "女卫生间出入口设落地镜；男卫生间小便器支撑抓杆与下口前缘距墙距离一致"},
    ],
    "无障碍厕所": [
        {"clause_number": "6.3.2.1a", "max_score": 1, "description": "采用推拉门"},
        {"clause_number": "6.3.2.1b", "max_score": 1, "description": "内部设婴儿打理台和儿童安全座椅"},
        {"clause_number": "6.3.2.1c", "max_score": 1, "description": "内设长度≥1.5m、宽度≥600mm、高度400~450mm的多功能床"},
        {"clause_number": "6.3.2.1d", "max_score": 1, "description": "设紧急情况声光报警灯"},
        {"clause_number": "6.3.2.2", "max_score": 1, "description": "门口无高差和门槛"},
        {"clause_number": "6.3.2.3a", "max_score": 0.5, "description": "两侧安全抓杆间距700mm~750mm"},
        {"clause_number": "6.3.2.3b", "max_score": 0.5, "description": "坐便器冲水装置为感应式自动冲水"},
        {"clause_number": "6.3.2.3c", "max_score": 0.5, "description": "轮椅靠近一侧有不小于700mm宽的移动空间"},
        {"clause_number": "6.3.2.3d", "max_score": 0.5, "description": "取纸器竖向中心线位于坐便器前端≤250mm处"},
        {"clause_number": "6.3.2.3e", "max_score": 1, "description": "设坐姿和倒地高度两处紧急呼叫按钮或拉绳"},
        {"clause_number": "6.3.2.4", "max_score": 2, "description": "无障碍洗手盆符合6.3.1.3要求"},
    ],
    "居室": [
        {"clause_number": "7.3.1.1", "max_score": 1, "description": "住宅入口门厅设有扶手和坐凳，空间满足乘轮椅者通行"},
        {"clause_number": "7.3.1.2", "max_score": 2, "description": "起居室、卧室（至少一间）均设直径≥1.5m轮椅回转空间"},
        {"clause_number": "7.3.1.3", "max_score": 1, "description": "起居室、卧室（至少一间）窗前通道宽度>800mm"},
        {"clause_number": "7.3.1.4a", "max_score": 0.5, "description": "至少一张床两侧均留出1.2m宽通道"},
        {"clause_number": "7.3.1.4b", "max_score": 1, "description": "床垫顶面高度400~450mm"},
        {"clause_number": "7.3.1.4c", "max_score": 0.5, "description": "床/床架和地板之间留出容脚空间（深度和高度均≥250mm）"},
        {"clause_number": "7.3.1.5a", "max_score": 1, "description": "家具位置、高度和容膝容脚空间方便乘轮椅者靠近和使用"},
        {"clause_number": "7.3.1.5b", "max_score": 1, "description": "家具无锋利棱角"},
        {"clause_number": "7.3.1.5c", "max_score": 1, "description": "衣橱内设低位挂衣杆（距地≤1.20m），内部安装照明"},
        {"clause_number": "7.3.1.6", "max_score": 1, "description": "地面未使用地毯，或使用绒毛高度<9mm地毯并固定"},
    ],
    "无障碍卫生间": [
        {"clause_number": "7.3.2.1", "max_score": 2, "description": "与无障碍卧室相邻布置，或在卧室中独立设置"},
        {"clause_number": "7.3.2.2a", "max_score": 2, "description": "内部设直径≥1.5m轮椅回转空间"},
        {"clause_number": "7.3.2.2b", "max_score": 2, "description": "无障碍坐便器符合6.3.2.3要求"},
        {"clause_number": "7.3.2.2c", "max_score": 2, "description": "无障碍洗手盆符合6.3.1.3要求"},
        {"clause_number": "7.3.2.2d", "max_score": 2, "description": "洗浴设施（淋浴间/盆浴间二选一）"},
    ],
    "公共浴室": [
        {"clause_number": "6.3.3.1", "max_score": 3, "description": "无障碍厕所或厕位设置情况（男女区分别设无障碍厕所3分/厕位2分/公共区1分）",
         "options": [{"label": "男女区分别设置无障碍厕所", "score": 3}, {"label": "男女区分别设置无障碍厕位", "score": 2}, {"label": "在公共区设置无障碍厕所", "score": 1}]},
        {"clause_number": "6.3.3.2a", "max_score": 1, "description": "乘轮椅者储物柜前设直径≥1.5m轮椅回转空间"},
        {"clause_number": "6.3.3.2b", "max_score": 1, "description": "储物柜开关装置距地0.85m~1.20m"},
        {"clause_number": "6.3.3.2c", "max_score": 1, "description": "更衣室长椅高度400mm~450mm，下方提供300mm高开放空间"},
        {"clause_number": "6.3.3.3a", "max_score": 1, "description": "淋浴间设固定座椅，有靠背和圆滑边缘"},
        {"clause_number": "6.3.3.3b", "max_score": 0.5, "description": "淋浴间内留有护理者操作空间"},
        {"clause_number": "6.3.3.3c", "max_score": 0.5, "description": "控制开关为杠杆型，配恒温器并有易识别记号"},
        {"clause_number": "6.3.3.4a", "max_score": 1, "description": "浴盆内侧设两层水平抓杆及L型安全抓杆"},
        {"clause_number": "6.3.3.4b", "max_score": 1, "description": "盆浴间控制开关为杠杆型，配恒温器并有易识别记号"},
    ],
    "轮椅席位": [
        {"clause_number": "6.3.4.1a", "max_score": 1, "description": "轮椅席位净尺寸宽度不小于900mm"},
        {"clause_number": "6.3.4.1b", "max_score": 1, "description": "轮椅席位边缘处安装栏杆或栏板"},
        {"clause_number": "6.3.4.1c", "max_score": 1, "description": "轮椅席位划出范围线并附地面标识"},
        {"clause_number": "6.3.4.1d", "max_score": 1, "description": "轮椅席位附近25m范围内设直径≥1.50m轮椅回转空间"},
        {"clause_number": "6.3.4.2", "max_score": 1, "description": "观众席装设1排以上可拆卸座椅"},
        {"clause_number": "6.3.4.3", "max_score": 2, "description": "低位服务设施无尖角、锐利边缘及过于粗糙表面"},
        {"clause_number": "6.3.4.4", "max_score": 2, "description": "低位服务设施前轮椅回转空间直径不小于1.50m"},
        {"clause_number": "6.3.4.5", "max_score": 1, "description": "低位服务设施底部容膝容脚空间宽度大于1.0m"},
    ],
}