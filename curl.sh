#!/usr/bin/env bash
# ==============================================================================
# FastAPI Homework - Test script for CRUD & Health Endpoints
# ==============================================================================

BASE_URL="http://127.0.0.1:8000"

echo "======================================================================"
echo "STARTING FASTAPI MINI HOMEWORK TESTS ON $BASE_URL"
echo "======================================================================"
echo ""

# 1. Liveness Probe
echo "1. Testing Liveness Probe (/health/live)..."
curl -s -X GET "$BASE_URL/health/live" -H "Accept: application/json"
echo -e "\n\n"

# 2. Readiness Probe
echo "2. Testing Readiness Probe (/health/ready)..."
curl -s -X GET "$BASE_URL/health/ready" -H "Accept: application/json"
echo -e "\n\n"

# 3. Create Item (Success Case)
echo "3. Testing Create Item (POST /items)..."
CREATE_RESP=$(curl -s -X POST "$BASE_URL/items" \
     -H "Content-Type: application/json" \
     -d '{
           "title": "Sach Lap trinh Python",
           "price": 150000.0,
           "discount_price": 120000.0
         }')
echo "$CREATE_RESP"
ITEM_ID=$(echo "$CREATE_RESP" | grep -o '"id":[0-9]*' | head -n 1 | cut -d':' -f2)
ITEM_ID=${ITEM_ID:-1}
echo -e "\nCreated Item ID: $ITEM_ID\n"

# 4. Test Pydantic V2 Validation Error
echo "4. Testing Pydantic V2 Validation Error (discount_price >= price)..."
curl -s -X POST "$BASE_URL/items" \
     -H "Content-Type: application/json" \
     -d '{
           "title": "Invalid Item",
           "price": 100.0,
           "discount_price": 200.0
         }'
echo -e "\n\n"

# 5. Get List of Items
echo "5. Testing Get List of Items (GET /items)..."
curl -s -X GET "$BASE_URL/items" -H "Accept: application/json"
echo -e "\n\n"

# 6. Get Item Detail
echo "6. Testing Get Item Detail (GET /items/$ITEM_ID)..."
curl -s -X GET "$BASE_URL/items/$ITEM_ID" -H "Accept: application/json"
echo -e "\n\n"

# 7. Update Item
echo "7. Testing Update Item (PUT /items/$ITEM_ID)..."
curl -s -X PUT "$BASE_URL/items/$ITEM_ID" \
     -H "Content-Type: application/json" \
     -d '{
           "title": "Sach Lap trinh Python FastAPI V2",
           "price": 180000.0,
           "discount_price": 140000.0
         }'
echo -e "\n\n"

# 8. Delete Item
echo "8. Testing Delete Item (DELETE /items/$ITEM_ID)..."
curl -s -X DELETE "$BASE_URL/items/$ITEM_ID" -H "Accept: application/json"
echo -e "\n\n"

# 9. Verify Deletion (404)
echo "9. Verifying Item Deletion (GET /items/$ITEM_ID)..."
curl -s -X GET "$BASE_URL/items/$ITEM_ID" -H "Accept: application/json"
echo -e "\n\n"

echo "======================================================================"
echo "ALL API TESTS COMPLETED!"
echo "======================================================================"
