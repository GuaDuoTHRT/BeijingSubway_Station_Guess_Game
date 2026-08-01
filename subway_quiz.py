#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
北京地铁站猜谜（命令行版）
题库文件：stations.json（与脚本同目录）
数据格式：[{"name": "林萃桥站", "lines": ["8号线"], "region": "北京北部", "ridership": "高", "formation": "6B"}, ...]
"""

import json
import random
import os


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 将题库文件路径设置为脚本同目录下的 stations.json
DATA_FILE = os.path.join(SCRIPT_DIR, "stations.json")

DEFAULT_STATIONS = [
    {"name": "林萃桥站", "lines": ["8号线"], "region": "北京北部", "ridership": "高", "formation": "6B"},
    {"name": "生命科学园站", "lines": ["昌平线"], "region": "北京北部", "ridership": "中", "formation": "6B"},
    {"name": "国贸站", "lines": ["1号线", "10号线"], "region": "北京中心", "ridership": "高", "formation": "6B"}
]


class SubwayQuiz:
    def __init__(self):
        self.stations = []
        self.total = 0
        self.correct = 0
        self.current_station = None
        self.current_clues = []
        self.answered = False

    def load_stations(self):
        print(f"当前目录：{os.getcwd()}")
        print(f"文件是否存在：{os.path.exists(DATA_FILE)}")
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_STATIONS, f, ensure_ascii=False, indent=2)
            print(f"📄 已创建默认题库文件：{DATA_FILE}，请根据需要编辑它。")
            self.stations = DEFAULT_STATIONS.copy()
        else:
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, list) or not data:
                    print("⚠️ 题库文件格式错误或为空，使用默认数据。")
                    self.stations = DEFAULT_STATIONS.copy()
                else:
                    # 按 name 去重
                    seen = set()
                    unique = []
                    for item in data:
                        name = item.get("name")
                        if name and name not in seen:
                            seen.add(name)
                            unique.append(item)
                    self.stations = unique
                    if len(unique) < len(data):
                        print(f"🔄 已自动去除 {len(data) - len(unique)} 个重复站名。")
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ 读取题库文件失败：{e}，使用默认数据。")
                print(f"⚠️ 读取题库文件失败：{e}")   # 加上这行
                self.stations = DEFAULT_STATIONS.copy()

    def generate_station_clue(self, station_name):
        """
        随机生成一条站名相关线索：
        - 要么是“拼音首字母是 X”
        - 要么是“第 N 个字是 ‘某’”
        （不包含字数信息）
        """
        name = station_name.replace("站", "")
        if not name:
            return "站名无效"

        options = []

        # 1. 首字母（使用简化的拼音映射）
        pinyin_map = {
            '安':'A','八':'B','巴':'B','白':'B','百':'B','北':'B','草':'C','车':'C',
            '长':'C','常':'C','朝':'C','成':'C','慈':'C','大':'D','德':'D','灯':'D',
            '定':'D','东':'D','豆':'D','垡':'F','方':'F','丰':'F','俸':'F','福':'F',
            '富':'F','甘':'G','高':'G','公':'G','宫':'G','巩':'G','鼓':'G','故':'G',
            '光':'G','广':'G','郭':'G','国':'G','海':'H','和':'H','河':'H','黑':'H',
            '红':'H','后':'H','呼':'H','胡':'H','虎':'H','花':'H','华':'H','化':'H',
            '黄':'H','惠':'H','火':'H','霍':'H','机':'J','积':'J','基':'J','纪':'J',
            '蓟':'J','嘉':'J','建':'J','健':'J','将':'J','焦':'J','角':'J','金':'J',
            '锦':'J','劲':'J','经':'J','九':'J','旧':'J','军':'J','开':'K','看':'K',
            '科':'K','可':'K','克':'K','空':'K','口':'K','来':'L','蓝':'L','郎':'L',
            '老':'L','乐':'L','雷':'L','梨':'L','礼':'L','李':'L','里':'L','立':'L',
            '丽':'L','利':'L','连':'L','莲':'L','两':'L','亮':'L','林':'L','临':'L',
            '灵':'L','刘':'L','柳':'L','六':'L','龙':'L','路':'L','潞':'L','马':'M',
            '麦':'M','毛':'M','门':'M','蒙':'M','孟':'M','米':'M','民':'M','木':'M',
            '南':'N','泥':'N','牛':'N','农':'N','潘':'P','庞':'P','平':'P','苹':'P',
            '蒲':'P','七':'Q','祈':'Q','前':'Q','墙':'Q','乔':'Q','桥':'Q','青':'Q',
            '清':'Q','区':'Q','屈':'Q','渠':'Q','全':'Q','群':'Q','人':'R','任':'R',
            '日':'R','荣':'R','三':'S','森':'S','沙':'S','山':'S','善':'S','上':'S',
            '芍':'S','少':'S','邵':'S','十':'S','石':'S','时':'S','实':'S','什':'S',
            '市':'S','首':'S','寿':'S','双':'S','水':'S','顺':'S','司':'S','四':'S',
            '宋':'S','苏':'S','孙':'S','台':'T','太':'T','潭':'T','唐':'T','陶':'T',
            '天':'T','田':'T','铁':'T','通':'T','同':'T','土':'T','团':'T','驼':'T',
            '万':'W','王':'W','望':'W','微':'W','韦':'W','魏':'W','温':'W','文':'W',
            '五':'W','武':'W','西':'X','希':'X','息':'X','喜':'X','下':'X','夏':'X',
            '先':'X','香':'X','向':'X','肖':'X','小':'X','孝':'X','协':'X','新':'X',
            '兴':'X','星':'X','行':'X','杏':'X','幸':'X','徐':'X','宣':'X','学':'X',
            '雪':'X','丫':'Y','亚':'Y','烟':'Y','延':'Y','闫':'Y','阎':'Y','燕':'Y',
            '羊':'Y','阳':'Y','杨':'Y','姚':'Y','药':'Y','亦':'Y','义':'Y','艺':'Y',
            '驿':'Y','益':'Y','意':'Y','殷':'Y','银':'Y','英':'Y','营':'Y','永':'Y',
            '勇':'Y','幽':'Y','游':'Y','友':'Y','于':'Y','余':'Y','鱼':'Y','雨':'Y',
            '玉':'Y','育':'Y','圆':'Y','远':'Y','月':'Y','悦':'Y','云':'Y','运':'Y',
            '枣':'Z','造':'Z','皂':'Z','泽':'Z','增':'Z','闸':'Z','张':'Z','章':'Z',
            '长':'Z','掌':'Z','丈':'Z','招':'Z','昭':'Z','朝':'Z','真':'Z','镇':'Z',
            '正':'Z','政':'Z','郑':'Z','知':'Z','织':'Z','直':'Z','植':'Z','址':'Z',
            '纸':'Z','志':'Z','制':'Z','中':'Z','钟':'Z','种':'Z','重':'Z','州':'Z',
            '周':'Z','朱':'Z','珠':'Z','诸':'Z','竹':'Z','主':'Z','祝':'Z','庄':'Z',
            '装':'Z','壮':'Z','追':'Z','准':'Z','卓':'Z','资':'Z','子':'Z','字':'Z',
            '自':'Z','宗':'Z','总':'Z','走':'Z','租':'Z','族':'Z','祖':'Z','钻':'Z',
            '最':'Z','尊':'Z','左':'Z','坐':'Z','做':'Z'
        }
        first_char = name[0] if name else ""
        initial = pinyin_map.get(first_char, first_char.upper())
        options.append(f"拼音首字母是 {initial}")

        # 2. 某个字（随机位置，只要站名长度>=2）
        if len(name) >= 2:
            pos = random.randint(1, len(name))  # 第几个字（1-based）
            char = name[pos-1]
            options.append(f"第{pos}个字是“{char}”")
        # 如果只有一个字，则只有首字母选项

        return random.choice(options)

    def generate_clues(self, station):
        """生成五条线索：线路、方位、站名相关、人流量、编组"""
        clues = []
        # 1. 线路
        lines = station.get("lines", [])
        if lines:
            line_str = "、".join(lines) if len(lines) > 1 else lines[0]
            clues.append(f"经过 {line_str}")
        else:
            clues.append("途经线路：未知")

        # 2. 方位
        region = station.get("region", "未知方位")
        clues.append(f"位于 {region}")

        # 3. 站名相关（随机）
        clues.append(self.generate_station_clue(station["name"]))

        # 4. 人流量
        ridership = station.get("ridership", "未知")
        clues.append(f"人流量 {ridership}")

        # 5. 编组
        formation = station.get("formation", "未知")
        clues.append(f"编组 {formation}")

        return clues

    def pick_station(self):
        if not self.stations:
            return None
        return random.choice(self.stations)

    def reset_round(self):
        self.current_station = self.pick_station()
        if not self.current_station:
            return False
        self.current_clues = self.generate_clues(self.current_station)
        self.answered = False
        return True
        print(self.current_station)   # 查看字典内容

    def display_clues(self):
        print("\n🔍 线索如下：")
        for i, clue in enumerate(self.current_clues, 1):
            print(f"  {i}. {clue}")

    def guess(self, user_input):
        if self.answered:
            print("⏳ 这一站已经猜过了，输入 '1' 继续下一题。")
            return
        normalized = user_input.strip().replace(" ", "")
        if not normalized.endswith("站"):
            normalized += "站"
        self.total += 1
        if normalized == self.current_station["name"]:
            self.correct += 1
            self.answered = True
            print(f"\n✅ 完全正确！就是 **{self.current_station['name']}** ！🎉")
        else:
            print(f"\n❌ 不对哦，再想想～ 你输入的是 “{normalized}”")

    def show_stats(self):
        rate = 0 if self.total == 0 else round((self.correct / self.total) * 100)
        print(f"\n📊 已猜 {self.total} 站 | 正确 {self.correct} 站 | 正确率 {rate}%")

    def run(self):
        self.load_stations()
        if not self.stations:
            print("❌ 无可用题库，程序退出。")
            return

        print("🚇 欢迎来到北京地铁站猜谜游戏！")
        print("💡 输入完整站名（含“站”字），如：林萃桥站")
        print("📌 数字命令： 0=退出  1=下一题  2=查看成绩\n")
        print("Made by @呱瓜多米; Made with DeepseekAI。欢迎反馈问题或建议。")
        print("反馈方式：在Github告诉我或者在Bilibili私信我。\n")
        print("\n")

        while True:
            if not self.reset_round():
                break
            self.display_clues()

            while True:
                user_input = input("\n👉 你的答案（或数字命令）：").strip()
                if user_input == "0":
                    print("👋 再见！")
                    self.show_stats()
                    return
                elif user_input == "1":
                    print("⏭️ 已跳过本题。")
                    if not self.answered:
                        print(f"🔎 正确答案是：{self.current_station['name']}")
                    break
                elif user_input == "2":
                    self.show_stats()
                    continue
                else:
                    self.guess(user_input)
                    if self.answered:
                        break

            self.show_stats()
            print("\n" + "-" * 40)

if __name__ == "__main__":
    quiz = SubwayQuiz()
    quiz.run()