import os
import subprocess
import tempfile

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from jinja2 import Template

from app.core.database import get_db
from app.services.crud import BuildingService, DimensionScoreService
from app.services.suggestion_service import build_improvement_suggestions
from app.data.priority_data import PRIORITY_CATEGORIES

router = APIRouter(prefix="/reports", tags=["评价报告"])

GRADE_LABELS = {
    "one_star": "一星级",
    "two_star": "二星级",
    "three_star": "三星级",
    "none": "未达标",
}

BUILDING_TYPE_LABELS = {
    "residential": "住宅类居住建筑",
    "non_residential": "非住宅类居住建筑",
    "public_with_accom": "含住宿功能的公共建筑",
    "public_no_accom": "不含住宿功能的公共建筑",
}

REPORT_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>无障碍设施评价报告 - {{ building.building_name }}</title>
<style>
body { font-family: "PingFang SC", "Microsoft YaHei", sans-serif; max-width: 800px; margin: 2em auto; padding: 0 1em; color: #333; }
h1 { text-align: center; font-size: 1.5em; }
table { width: 100%; border-collapse: collapse; margin: 1em 0; }
th, td { border: 1px solid #999; padding: 6px 10px; text-align: left; }
th { background: #f0f0f0; }
.grade { font-size: 1.3em; font-weight: bold; text-align: center; padding: 0.5em; }
.meta { color: #666; font-size: 0.9em; text-align: center; }
</style>
</head>
<body>
<h1>民用建筑无障碍设施评价报告</h1>
<p class="meta">依据 T/CNAEC 1304—2022《民用建筑无障碍设施评价标准》</p>

<h2>一、建筑信息</h2>
<table>
<tr><th>建筑名称</th><td>{{ building.building_name }}</td></tr>
<tr><th>建筑类型</th><td>{{ building_type_label }}</td></tr>
<tr><th>建筑面积</th><td>{{ building.floor_area or "—" }} ㎡</td></tr>
<tr><th>评价时间</th><td>{{ score.calculated_at.strftime("%Y-%m-%d %H:%M") }}</td></tr>
</table>

<h2>二、维度得分</h2>
<table>
<tr><th>维度</th><th>系统分 S</th><th>设施分 F</th><th>维度分 Q</th></tr>
<tr><td>Q1 无障碍通行</td><td>{{ score.q1_system_score }}</td><td>{{ score.q1_facility_score }}</td><td>{{ score.q1_score }}</td></tr>
{% if score.q2_score is not none %}
<tr><td>Q2 公共无障碍服务</td><td>{{ score.q2_system_score }}</td><td>{{ score.q2_facility_score }}</td><td>{{ score.q2_score }}</td></tr>
{% endif %}
{% if score.q3_score is not none %}
<tr><td>Q3 无障碍住宿</td><td>{{ score.q3_system_score }}</td><td>{{ score.q3_facility_score }}</td><td>{{ score.q3_score }}</td></tr>
{% endif %}
<tr><td>Q4 信息交流</td><td colspan="2">—</td><td>{{ score.q4_score }}</td></tr>
<tr><td>Q5 创新提升</td><td colspan="2">—</td><td>{{ score.q5_score }}</td></tr>
<tr><td>施工验收</td><td colspan="2">—</td><td>{{ score.construction_score }}</td></tr>
<tr><td>运行维护</td><td colspan="2">—</td><td>{{ score.maintenance_score }}</td></tr>
</table>

<h2>三、评价结论</h2>
<table>
<tr><th>总体评价分 Q</th><td>{{ score.total_score_q }}</td></tr>
</table>
<p class="grade">评价等级：{{ grade_label }}</p>

{% if suggestions %}
<h2>四、短板改善建议（按改造优先级排序）</h2>
<table>
<tr><th>优先级</th><th>目标</th><th>改造类别</th><th>改造内容</th><th>条文号</th><th>现状</th><th>失分</th></tr>
{% for s in suggestions %}
<tr>
<td>{{ "★" * s.stars }}</td>
<td>{% if s.is_key %}<strong style="color:#b91c1c;">升星关键</strong>{% else %}提升总分{% endif %}</td>
<td>{{ s.category }}</td>
<td>{{ s.content }}</td>
<td>{{ s.clause_number }}</td>
<td>{{ s.status }}</td>
<td>{{ s.lost_score if s.lost_score is not none else "—" }}</td>
</tr>
{% endfor %}
</table>
{% endif %}
</body>
</html>""")


@router.get("/building/{building_id}", response_class=HTMLResponse)
def get_building_report(building_id: str, db: Session = Depends(get_db)):
    """生成单体建筑评价报告（HTML）"""
    building = BuildingService.get(db, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="建筑不存在")
    score = DimensionScoreService.get_latest(db, building_id)
    if not score:
        raise HTTPException(status_code=404, detail="该建筑尚无评价结果，请先执行评价计算")

    grade_value = score.determined_grade.value if score.determined_grade else "none"
    return REPORT_TEMPLATE.render(
        building=building,
        score=score,
        grade_label=GRADE_LABELS.get(grade_value, grade_value),
        building_type_label=BUILDING_TYPE_LABELS.get(
            building.building_type.value, building.building_type.value
        ),
        suggestions=build_improvement_suggestions(db, building_id)["suggestions"],
    )

@router.get("/building/{building_id}/suggestions")
def get_improvement_suggestions(building_id: str, db: Session = Depends(get_db)):
    """获取短板改善建议（按改造优先级排序）"""
    building = BuildingService.get(db, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="建筑不存在")
    result = build_improvement_suggestions(db, building_id)
    result["building_id"] = building_id
    return result


_CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
]


def _find_chrome():
    for p in _CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


@router.get("/building/{building_id}/pdf")
def get_building_report_pdf(building_id: str, db: Session = Depends(get_db)):
    """生成单体建筑评价报告（PDF，经无头Chrome打印）"""
    building = BuildingService.get(db, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="建筑不存在")
    score = DimensionScoreService.get_latest(db, building_id)
    if not score:
        raise HTTPException(status_code=404, detail="该建筑尚无评价结果，请先执行评价计算")

    chrome = _find_chrome()
    if not chrome:
        raise HTTPException(status_code=500, detail="服务器未安装Chrome，无法生成PDF")

    grade_value = score.determined_grade.value if score.determined_grade else "none"
    html = REPORT_TEMPLATE.render(
        building=building,
        score=score,
        grade_label=GRADE_LABELS.get(grade_value, grade_value),
        building_type_label=BUILDING_TYPE_LABELS.get(
            building.building_type.value, building.building_type.value
        ),
        suggestions=build_improvement_suggestions(db, building_id)["suggestions"],
    )

    tmp_dir = tempfile.mkdtemp(prefix="report_")
    html_path = os.path.join(tmp_dir, "report.html")
    pdf_path = os.path.join(tmp_dir, "report.pdf")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    try:
        subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
             f"--print-to-pdf={pdf_path}", html_path],
            check=True, capture_output=True, timeout=60,
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"PDF生成失败: {e.stderr.decode()[:200]}")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"无障碍评价报告_{building.building_name}.pdf",
    )
