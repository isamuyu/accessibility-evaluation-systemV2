#!/bin/bash

echo "================================"
echo "无障碍设施评价系统 - 快速测试"
echo "================================"
echo ""

API="http://localhost:8000"

# 1. 创建项目
echo "1. 创建测试项目..."
PROJECT=$(curl -s -X POST "$API/projects/" \
  -H "Content-Type: application/json" \
  -d '{"project_name": "演示项目", "evaluation_type": "initial", "applicant_name": "测试用户"}')
PROJECT_ID=$(echo $PROJECT | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "   项目ID: $PROJECT_ID"

# 2. 创建建筑
echo ""
echo "2. 添加建筑..."
BUILDING=$(curl -s -X POST "$API/buildings/" \
  -H "Content-Type: application/json" \
  -d "{\"project_id\": \"$PROJECT_ID\", \"building_name\": \"1号楼\", \"building_type\": \"public_no_accom\", \"floor_area\": 20000, \"is_within_one_year\": true}")
BUILDING_ID=$(echo $BUILDING | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "   建筑ID: $BUILDING_ID"

# 3. 添加控制项
echo ""
echo "3. 录入控制项..."
curl -s -X POST "$API/scoring/control-items/$BUILDING_ID" \
  -H "Content-Type: application/json" \
  -d '{"clause_id": "5.1.1.1", "chapter": "Q1", "is_compliant": true}' > /dev/null
curl -s -X POST "$API/scoring/control-items/$BUILDING_ID" \
  -H "Content-Type: application/json" \
  -d '{"clause_id": "5.1.1.2", "chapter": "Q1", "is_compliant": true}' > /dev/null
echo "   ✓ 控制项已录入"

# 4. 添加系统评分
echo ""
echo "4. 录入系统评分..."
curl -s -X POST "$API/scoring/system-scores/$BUILDING_ID" \
  -H "Content-Type: application/json" \
  -d '{"clause_id": "5.2.1.1", "chapter": "Q1", "max_score": 8, "applicable_score": 8, "actual_score": 8}' > /dev/null
curl -s -X POST "$API/scoring/system-scores/$BUILDING_ID" \
  -H "Content-Type: application/json" \
  -d '{"clause_id": "5.2.1.2", "chapter": "Q1", "max_score": 8, "applicable_score": 8, "actual_score": 6}' > /dev/null
curl -s -X POST "$API/scoring/system-scores/$BUILDING_ID" \
  -H "Content-Type: application/json" \
  -d '{"clause_id": "8.2.1.1", "chapter": "Q4", "max_score": 10, "applicable_score": 10, "actual_score": 10}' > /dev/null
curl -s -X POST "$API/scoring/system-scores/$BUILDING_ID" \
  -H "Content-Type: application/json" \
  -d '{"clause_id": "9.2.1.1", "chapter": "construction", "max_score": 20, "applicable_score": 20, "actual_score": 18}' > /dev/null
curl -s -X POST "$API/scoring/system-scores/$BUILDING_ID" \
  -H "Content-Type: application/json" \
  -d '{"clause_id": "10.2.1.1", "chapter": "maintenance", "max_score": 20, "applicable_score": 20, "actual_score": 16}' > /dev/null
echo "   ✓ 系统评分已录入"

# 5. 执行评价
echo ""
echo "5. 执行评价计算..."
RESULT=$(curl -s -X POST "$API/scoring/evaluate/$BUILDING_ID")
echo "   结果:"
echo "$RESULT" | python3 -m json.tool | sed 's/^/   /'

echo ""
echo "================================"
echo "测试完成！"
echo ""
echo "访问前端页面: http://localhost:8000/"
echo "查看API文档: http://localhost:8000/docs"
echo ""
echo "项目ID: $PROJECT_ID"
echo "建筑ID: $BUILDING_ID"
echo "================================"