from datetime import datetime, timezone
import json
from pathlib import Path

OUT = Path("collectible-facts.json")

# 仅使用可核验的基础知识作为每日内容池；每日按日期轮换，避免虚构“今日发生”的事件。
FACTS = [
    {"title":"为什么古钱币中间常有方孔？", "text":"方孔圆钱的形制长期流行，既便于穿绳携带，也形成了中国古代货币极具辨识度的视觉符号。不同朝代的文字、书体、铸造工艺和钱文布局，都是收藏研究的重要线索。", "tag":"古钱知识"},
    {"title":"一枚银元为什么不能只看正面？", "text":"银元鉴定通常需要结合正背面、边齿、重量、直径、包浆与铸造细节综合判断。边齿和细节往往能提供重要的版别与真伪线索。", "tag":"银元鉴定"},
    {"title":"钱币品相为什么会影响价格？", "text":"同一基本品种在磨损程度、原光、包浆、划痕、清洗、修补等方面存在差异时，收藏市场的价格区间可能明显不同。因此价格表应尽量按品种与品相分层。", "tag":"收藏知识"},
    {"title":"评级币的数字代表什么？", "text":"PCGS、NGC、PMG等评级体系会对不同类别的收藏品进行鉴定和品相评级。看到评级数字时，还应结合币种、版别、特殊状态及市场成交情况综合判断。", "tag":"评级知识"},
    {"title":"为什么老纸币要特别注意号码和版别？", "text":"纸币价值除了品相，还可能受到版别、冠号、号码、水印、暗记及稀缺程度等因素影响。价格比较时不能只依据面值或纸币名称。", "tag":"纸币知识"},
    {"title":"收藏钱币时为什么要记录成交时间？", "text":"钱币价格具有时间属性。同一品种在不同年份、不同品相和不同交易渠道的价格可能不同，因此建立带日期的成交样本，比单独记录一个静态价格更有参考意义。", "tag":"行情研究"},
    {"title":"泉州为什么适合做钱币收藏交流？", "text":"泉州拥有丰富的海丝文化与民间收藏传统。钱币收藏可以从地方历史、贸易文化、铸币制度和民间流通等角度展开研究，本地交流与全国市场数据结合更有价值。", "tag":"泉州收藏"},
]

def main():
    now = datetime.now(timezone.utc).astimezone()
    item = FACTS[now.timetuple().tm_yday % len(FACTS)]
    data = {
        "date": now.strftime("%Y-%m-%d"),
        "updated_at": now.isoformat(timespec="minutes"),
        "title": item["title"],
        "text": item["text"],
        "tag": item["tag"],
        "note": "AI每日整理；内容为收藏知识与研究参考，不构成鉴定或价格承诺。"
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
