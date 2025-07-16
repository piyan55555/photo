from PIL import Image, ImageDraw
import numpy as np

# 五區座標（圖片 resize 成 300x400 後使用）
zones = {
    "舌尖（心肺）": [(110, 310), (190, 310), (180, 350), (120, 350)],
    "膽": [(60, 180), (100, 260), (130, 260), (100, 180)],
    "脾胃": [(130, 150), (130, 260), (170, 260), (170, 150)],
    "肝": [(170, 180), (200, 260), (240, 260), (200, 180)],
    "腎": [(100, 80), (200, 80), (200, 130), (100, 130)]
}

# 色彩分類與中醫對應建議
color_map = {
    "黃色": "火氣大，需調理肝膽系統",
    "白色厚重": "濕氣重，可能為代謝循環不佳",
    "黑灰色": "請留意嚴重疾病如腎病或癌症",
    "正常舌色": "正常紅舌或紅帶薄白，健康狀態",
    "未知": "色彩無法明確分類，建議重新拍攝或補光"
}

# RGB → 顏色分類
def determine_category_from_rgb(r, g, b):
    brightness = (r + g + b) / 3
    if r > 130 and g < 140 and b < 140 and brightness < 190:
        return "正常舌色"
    elif r > 140 and g > 110 and b < 100 and brightness > 150:
        return "黃色"
    elif brightness > 180 and min(r, g, b) > 160:
        return "白色厚重"
    elif brightness < 100 and max(abs(r - g), abs(g - b), abs(r - b)) < 60:
        return "黑灰色"
    else:
        return "未知"

# 將多邊形轉成遮罩
def poly_to_mask(size, polygon):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).polygon(polygon, outline=1, fill=1)
    return np.array(mask)

# 分析五區顏色與中醫建議
def analyze_five_zones(image_path):
    image = Image.open(image_path).convert("RGB").resize((300, 400))
    img_array = np.array(image)
    result = {}

    for zone, poly in zones.items():
        mask = poly_to_mask((300, 400), poly)
        pixels = img_array[mask == 1]
        if len(pixels) == 0:
            avg = (0, 0, 0)
        else:
            avg = tuple(map(int, np.mean(pixels, axis=0)))
        cat = determine_category_from_rgb(*avg)
        result[zone] = {
            "RGB": avg,
            "顏色": cat,
            "推論": color_map.get(cat, "無法判斷")
        }

    return result

# 測試用：可用 CLI 執行
if __name__ == "__main__":
    from pprint import pprint
    res = analyze_five_zones("your_image.jpg")  # 替換為圖片檔名
    pprint(res)
