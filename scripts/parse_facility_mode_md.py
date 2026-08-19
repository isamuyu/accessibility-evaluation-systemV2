#!/usr/bin/env python3
"""解析《认证审查条款.md》为设施模式种子数据 JSON

md 结构：## 分类 → **条款 5.2 / 5.2.1 / （5.2.1.5）** → 内容(含子项/选项) → > **标准分值：N**
输出：app/data/facility_mode_data.json
"""
import json
import re
import sys

MD_PATH = "/Users/isamu/workbuddy/20260418140457/认证审查条款.md"
OUT_PATH = "app/data/facility_mode_data.json"

# 跳过的重复类别（与旧版一致）
SKIP_CATEGORIES = {"无障碍厕所2", "门2-无障碍厕所1-自动门", "门3-无障碍厕所2-手动门"}

# 公共浴室和更衣室的子章节合并（与旧版一致）
MERGE_BATHROOM = re.compile(r"^公共浴室和更衣室")

# 类别编码（按目录顺序，与旧版 TOC_CATEGORY_MAP 一致；public_bathroom 由合并分支单独赋值，不在此序列）
CATEGORY_CODES = [
    "landscaping", "tactile_path", "curb_ramp", "handrail", "residential_road",
    "residential_green", "accessible_parking", "accessible_circulation", "access_passage",
    "wheelchair_ramp", "entrance_ratio", "access_entrance", "door_config", "door_main",
    "public_rest_area", "wheelchair_seat", "low_service", "elevator_basic", "elevator_detail",
    "stairs_steps", "sanitary_facility", "public_toilet", "toilet_stall", "toilet_basin",
    "toilet_urinal", "accessible_toilet_1", "nursing_room", "family_toilet",
    "info_service", "accessible_accommodation",
]

CHAPTER_BY_PREFIX = {
    "5": "Q1", "6": "Q2", "7": "Q3", "8": "Q4",
    "9": "construction", "10": "maintenance", "11": "Q5",
}


def clause_type_of(std_number: str) -> str:
    """按标准条款号判定类型：5-10章的 x.1.1 为控制项，5.3/6.3/7.3 为设施项，其余为系统项（11章为Q5加分项，无控制项）"""
    parts = std_number.split(".")
    if parts[0] in ("5", "6", "7", "8", "9", "10") and len(parts) >= 3 \
            and parts[1] == "1" and parts[2].startswith("1"):
        return "control"
    if len(parts) >= 2 and parts[1] == "3" and parts[0] in ("5", "6", "7"):
        return "facility"
    return "system"


def chapter_of(std_number: str) -> str:
    return CHAPTER_BY_PREFIX.get(std_number.split(".")[0], "Q1")


def parse_std_number(line: str) -> str:
    """从 **条款 5.3 / 5.3.6 / （5.3.6.2，d）** 提取标准条款号 -> 5.3.6.2d"""
    m = re.search(r"[（(]([0-9.]+)[，,]?\s*([a-z])?\s*[）)]", line)
    if not m:
        return ""
    num = m.group(1).rstrip(".")
    suffix = m.group(2) or ""
    return num + suffix


def parse_clause_body(body: str) -> dict:
    """解析条款正文：子项(累计)、单选选项、布尔"""
    # 子项: a）【标题】内容 ○是（+2分）○否○不参评
    sub_items = []
    for m in re.finditer(
        r"([a-z])）\s*(?:【([^】]+)】)?(.{0,120}?)[○●]?\s*是[（(]\s*\+?\s*([0-9.]+)\s*分\s*[)）]",
        body, re.S
    ):
        label = (m.group(2) or "").strip()
        if not label:
            label = re.sub(r"\s+", "", m.group(3))[:30]
        sub_items.append({"label": label, "score": float(m.group(4))})

    if sub_items:
        return {"score_type": "multiple", "sub_items": sub_items}

    # 单选选项: ○标签（+N分）
    options = []
    for m in re.finditer(r"[○●]\s*([^○●\n（(]+?)[（(]\+?([0-9.]+)\s*分[)）]", body):
        label = re.sub(r"\s+", "", m.group(1))
        if label and label not in ("是", "否", "不参评"):
            options.append({"label": label, "score": float(m.group(2))})

    # 布尔: 是（+N分） / 无选项的单纯是否
    bool_m = re.search(r"[○●]?是[（(]\+?([0-9.]+)\s*分[)）]", body)
    if options:
        # 含"是（+N分）"以外的多个选项才算单选
        if bool_m and len(options) <= 1:
            return {"score_type": "boolean"}
        return {"score_type": "single_choice", "options": options}
    if bool_m:
        return {"score_type": "boolean"}
    return {"score_type": "boolean"}  # 兜底


def main():
    text = open(MD_PATH, encoding="utf-8").read()

    # 按 ## 切分类别（跳过目录）
    sections = re.split(r"\n## ", text)
    categories = []
    clauses = []
    code_idx = 0

    for sec in sections[1:]:
        lines = sec.strip().split("\n")
        cat_name = lines[0].strip()
        if cat_name in ("目录",) or cat_name.startswith(">"):
            continue
        if cat_name in SKIP_CATEGORIES:
            continue

        if MERGE_BATHROOM.match(cat_name):
            code = "public_bathroom"
            cat_name_final = "公共浴室和更衣室"
        else:
            if code_idx >= len(CATEGORY_CODES):
                print(f"⚠ 类别超出编码表: {cat_name}", file=sys.stderr)
                continue
            code = CATEGORY_CODES[code_idx]
            cat_name_final = cat_name
            code_idx += 1

        if not any(c["category_code"] == code for c in categories):
            categories.append({"category_code": code, "category_name": cat_name_final})

        # 按 **条款 切分
        blocks = re.split(r"\n\*\*条款 ", sec)
        for bi, block in enumerate(blocks[1:], 1):
            first_line = block.split("\n")[0]
            std_number = parse_std_number(first_line)
            if not std_number:
                continue
            body = "\n".join(block.split("\n")[1:])
            body = re.sub(r"> \*\*标准分值.*", "", body).strip()
            parsed = parse_clause_body(body)
            max_m = re.search(r"标准分值[：:]\s*([0-9.]+)", block)

            # 标题取正文首个【】
            title_m = re.search(r"【([^】]+)】", body)
            base_cn = f"{code}-{std_number}"
            clause_number = base_cn
            n = 2
            existing = {c["clause_number"] for c in clauses}
            while clause_number in existing:
                clause_number = f"{base_cn}~{n}"
                n += 1
            clauses.append({
                "clause_number": clause_number,
                "standard_clause_number": std_number,
                "category_code": code,
                "chapter": chapter_of(std_number),
                "clause_type": clause_type_of(std_number),
                "title": title_m.group(1) if title_m else cat_name_final,
                "content": re.sub(r"\*\*|\n{2,}", "", body).replace("\n", " ").strip()[:500],
                "max_score": float(max_m.group(1)) if max_m else 0,
                "score_type": parsed["score_type"],
                "score_options": {k: v for k, v in parsed.items() if k != "score_type"} or None,
                "sort_order": bi,
            })

    out = {"categories": categories, "clauses": clauses}
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print(f"类别: {len(categories)}  条款: {len(clauses)}")
    from collections import Counter
    print("类型分布:", dict(Counter(c["clause_type"] for c in clauses)))
    print("评分类型:", dict(Counter(c["score_type"] for c in clauses)))
    print("章节分布:", dict(Counter(c["chapter"] for c in clauses)))


if __name__ == "__main__":
    main()
