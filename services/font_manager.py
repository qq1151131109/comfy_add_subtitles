"""
字体管理器
动态检测和管理系统字体，解决不同字体显示相同的问题
"""

import os
import subprocess
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import tempfile
from PIL import Image, ImageDraw, ImageFont


class FontManager:
    """字体管理器 - 动态检测和管理系统字体，支持多语种分类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._font_cache = {}
        self._available_fonts = None
        self._categorized_fonts = None
        self.font_validation_cache = {}
        self._font_language_cache = {}
        
    def get_available_fonts(self) -> List[str]:
        """获取系统实际可用的字体列表"""
        if self._available_fonts is not None:
            return self._available_fonts
            
        try:
            # 使用 fc-list 命令获取系统字体
            result = subprocess.run(
                ['fc-list', ':', 'family'],
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.logger.warning("fc-list 命令执行失败，使用默认字体列表")
                return self._get_fallback_fonts()
            
            # 解析字体列表
            fonts = set()
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    # 处理字体名称，取第一个名称（通常是英文名）
                    family_names = line.split(',')
                    if family_names:
                        font_name = family_names[0].strip()
                        if font_name and not font_name.startswith('.'):  # 排除隐藏字体
                            fonts.add(font_name)
            
            # 按字体类型分类并排序
            categorized_fonts = self._categorize_fonts(list(fonts))
            self._available_fonts = categorized_fonts
            
            self.logger.info(f"检测到 {len(self._available_fonts)} 种可用字体")
            return self._available_fonts
            
        except Exception as e:
            self.logger.error(f"获取系统字体时发生错误: {e}")
            return self._get_fallback_fonts()
    
    def _detect_font_language(self, font_name: str) -> str:
        """检测字体的主要语种"""
        font_lower = font_name.lower()
        
        # 优先检查中文字体（包括繁体中文字符）
        chinese_chars = ['文泉', '微米黑', '正黑', '點陣', '等寬', '驛', '驿', '泉', '微米', '点阵', '等宽']
        for char_set in chinese_chars:
            if char_set in font_name:  # 直接检查原字体名，不转小写
                return 'chinese'
        
        # 英文拼音的中文字体识别
        chinese_keywords = ['wenquan', 'wqy', 'micro hei', 'zen hei']
        for keyword in chinese_keywords:
            if keyword in font_lower:
                return 'chinese'
        
        # 日文字体识别 - 必须在CJK之前检查
        if 'jp' in font_lower:
            return 'japanese'
        japanese_keywords = ['japan', 'hiragino', 'mincho', 'gothic', 'osaka', 'yu gothic', 'yu mincho']
        for keyword in japanese_keywords:
            if keyword in font_lower:
                return 'japanese'
                
        # 韩文字体识别 - 必须在CJK之前检查
        if 'kr' in font_lower:
            return 'korean'
        korean_keywords = ['korea', 'malgun', 'gulim', 'batang']
        for keyword in korean_keywords:
            if keyword in font_lower:
                return 'korean'
        
        # 中文字体识别（简体）
        if 'sc' in font_lower or 'cn' in font_lower:
            return 'chinese'
            
        # 中文字体识别（繁体） 
        if 'hk' in font_lower or 'tc' in font_lower or 'tw' in font_lower:
            return 'chinese'
        
        # CJK 通用字体 - 如果没有明确的国家标识，默认为中文
        if 'cjk' in font_lower:
            return 'chinese'
                
        # 阿拉伯字体识别
        arabic_keywords = ['arab', 'naskh', 'kufi', 'amiri']
        for keyword in arabic_keywords:
            if keyword in font_lower:
                return 'arabic'
                
        # 符号字体识别
        symbol_keywords = ['emoji', 'symbol', 'awesome', 'icon', 'material', 'nerd font', 'symbols']
        for keyword in symbol_keywords:
            if keyword in font_lower:
                return 'symbol'
            
        # 默认为英文/拉丁字体
        return 'latin'
    
    def get_font_language(self, font_name: str) -> str:
        """获取字体语种（带缓存）"""
        if font_name not in self._font_language_cache:
            self._font_language_cache[font_name] = self._detect_font_language(font_name)
        return self._font_language_cache[font_name]
    
    def get_fonts_by_language(self) -> Dict[str, List[str]]:
        """按语种分类获取字体"""
        if self._categorized_fonts is not None:
            return self._categorized_fonts
            
        all_fonts = self.get_available_fonts()
        categorized = {
            'latin': [],      # 英文/拉丁字体
            'chinese': [],    # 中文字体  
            'japanese': [],   # 日文字体
            'korean': [],     # 韩文字体
            'arabic': [],     # 阿拉伯字体
            'symbol': [],     # 符号字体
        }
        
        for font in all_fonts:
            language = self.get_font_language(font)
            if language in categorized:
                categorized[language].append(font)
            else:
                categorized['latin'].append(font)  # 未识别的归类为拉丁字体
                
        self._categorized_fonts = categorized
        return self._categorized_fonts
    
    def _categorize_fonts(self, fonts: List[str]) -> List[str]:
        """对字体进行分类和排序"""
        
        # 按语种分类
        fonts_by_lang = {}
        for font in fonts:
            lang = self._detect_font_language(font)
            if lang not in fonts_by_lang:
                fonts_by_lang[lang] = []
            fonts_by_lang[lang].append(font)
        
        # 定义各语种字体的详细优先级和分类
        font_priorities = {
            'latin': {
                # 经典无衬线字体
                'Arial': 100, 'Helvetica': 98, 'Helvetica Neue': 96,
                'Verdana': 94, 'Tahoma': 92, 'Calibri': 90,
                
                # 现代无衬线字体
                'Inter': 88, 'Roboto': 86, 'Open Sans': 84, 
                'Lato': 82, 'Lato Medium': 81, 'Lato Light': 80,
                'Source Sans Pro': 79, 'Nunito': 78,
                'Poppins': 76, 'Montserrat': 74, 'Ubuntu': 72,
                'Fira Sans': 70,
                
                # 系统字体 - Liberation系列
                'Liberation Sans': 68, 'Liberation Sans Narrow': 67,
                'DejaVu Sans': 66, 'Noto Sans': 64, 'Oxygen': 62,
                
                # 经典衬线字体
                'Times New Roman': 100, 'Times': 98, 'Georgia': 96,
                'Palatino': 94, 'Book Antiqua': 92, 'Garamond': 90,
                'Baskerville': 88, 'Caslon': 86,
                
                # 现代衬线字体
                'Source Serif Pro': 84, 'Merriweather': 82,
                'Playfair Display': 80, 'Lora': 78,
                
                # 系统衬线字体 - Liberation系列
                'Liberation Serif': 76, 'DejaVu Serif': 74,
                'Noto Serif': 72,
                
                # 等宽字体
                'Fira Code': 100, 'JetBrains Mono': 98, 'Source Code Pro': 96,
                'Monaco': 94, 'Consolas': 92, 'Menlo': 90,
                'Cascadia Code': 88, 'Hack': 86, 'Inconsolata': 84,
                'Ubuntu Mono': 82, 'DejaVu Sans Mono': 80,
                'Liberation Mono': 78, 'Courier New': 76, 'Courier': 74,
                
                # 显示字体和特殊字体
                'Impact': 100, 'Arial Black': 95, 'Bebas Neue': 90,
                'Oswald': 85, 'Russo One': 80, 'Anton': 75,
                'Comic Sans MS': 70, 'Papyrus': 60,
                
                # Lato 字体变体
                'Lato Black': 77, 'Lato Bold': 76, 'Lato Heavy': 75,
                'Lato Semibold': 74, 'Lato Thin': 73,
            },
            'chinese': {
                'WenQuanYi Zen Hei': 100, 'WenQuanYi Micro Hei': 95,
                'Noto Sans CJK SC': 90, 'Noto Serif CJK SC': 85,
                'Source Han Sans CN': 80, 'Source Han Serif CN': 75,
                'SimHei': 70, 'SimSun': 68, 'Microsoft YaHei': 65,
                'PingFang SC': 60, 'Hiragino Sans GB': 55,
            },
            'japanese': {
                'Noto Sans CJK JP': 100, 'Noto Serif CJK JP': 95,
                'Hiragino Kaku Gothic Pro': 90, 'Hiragino Mincho Pro': 85,
                'Yu Gothic': 80, 'Yu Mincho': 75,
            },
            'korean': {
                'Noto Sans CJK KR': 100, 'Noto Serif CJK KR': 95,
                'Malgun Gothic': 90, 'Gulim': 85, 'Batang': 80,
            },
            'symbol': {
                'FontAwesome': 100, 'Material Icons': 95,
                'Symbols Nerd Font': 90, 'Emoji One': 85,
            }
        }
        
        # 按语种和优先级排序字体
        final_fonts = []
        
        # 语种显示顺序：英文优先，然后中文，其他语种
        language_order = ['latin', 'chinese', 'japanese', 'korean', 'arabic', 'symbol']
        
        for lang in language_order:
            if lang not in fonts_by_lang:
                continue
                
            lang_fonts = fonts_by_lang[lang]
            if not lang_fonts:
                continue
                
            # 按优先级排序本语种的字体
            priority_fonts = font_priorities.get(lang, {})
            priority_found = []
            other_fonts = []
            
            for font in lang_fonts:
                if font in priority_fonts:
                    priority_found.append((font, priority_fonts[font]))
                else:
                    other_fonts.append(font)
            
            # 按优先级排序
            priority_found.sort(key=lambda x: x[1], reverse=True)
            sorted_priority_fonts = [font[0] for font in priority_found]
            
            # 其他字体按字母顺序
            other_fonts.sort()
            
            # 合并本语种的字体
            final_fonts.extend(sorted_priority_fonts)
            final_fonts.extend(other_fonts)
        
        return final_fonts
    
    def get_fonts_with_language_labels(self) -> List[str]:
        """获取带语种标注的字体列表"""
        fonts_by_language = self.get_fonts_by_language()
        labeled_fonts = []
        
        # 语种标签映射
        language_labels = {
            'latin': '🅰️',      # 英文/拉丁字体
            'chinese': '🀄',    # 中文字体
            'japanese': '🗾',   # 日文字体  
            'korean': '🇰🇷',    # 韩文字体
            'arabic': '🌙',     # 阿拉伯字体
            'symbol': '🔣',     # 符号字体
        }
        
        language_names = {
            'latin': 'EN',
            'chinese': 'CN', 
            'japanese': 'JP',
            'korean': 'KR',
            'arabic': 'AR',
            'symbol': 'SYM',
        }
        
        # 按顺序添加各语种字体
        for lang in ['latin', 'chinese', 'japanese', 'korean', 'arabic', 'symbol']:
            if lang in fonts_by_language and fonts_by_language[lang]:
                for font in fonts_by_language[lang]:
                    # 格式：[标签] 字体名称
                    label = language_names[lang]
                    labeled_font = f"[{label}] {font}"
                    labeled_fonts.append(labeled_font)
        
        return labeled_fonts
    
    def extract_font_name_from_label(self, labeled_font: str) -> str:
        """从带标签的字体名称中提取原始字体名称"""
        # 移除语种标签，提取原始字体名称
        if '] ' in labeled_font:
            return labeled_font.split('] ', 1)[1]
        return labeled_font
    
    def _get_fallback_fonts(self) -> List[str]:
        """获取回退字体列表"""
        return [
            "DejaVu Sans",
            "DejaVu Serif", 
            "DejaVu Sans Mono",
            "Liberation Sans",
            "Liberation Serif",
            "Liberation Mono",
            "WenQuanYi Zen Hei",
            "WenQuanYi Micro Hei",
            "Noto Sans",
            "Noto Serif",
            "Lato"
        ]
    
    def get_font_path(self, font_family: str, weight: str = 'regular') -> str:
        """
        获取指定字体的实际文件路径 - 环境无关版本
        
        Args:
            font_family: 字体族名称
            weight: 字体粗细 ('regular', 'bold', 'light', etc.)
            
        Returns:
            字体文件路径
        """
        cache_key = f"{font_family}:{weight}"
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        # 方法1: 尝试使用本地字体配置
        font_path = self._get_font_path_from_config(font_family, weight)
        if font_path:
            self._font_cache[cache_key] = font_path
            return font_path
        
        # 方法2: 尝试使用fc-match（如果可用）
        try:
            # 构造字体查询字符串，指定粗细
            if weight == 'bold':
                query = f"{font_family}:weight=bold"
            elif weight == 'light':
                query = f"{font_family}:weight=light"
            else:
                query = f"{font_family}:weight=regular"
            
            # 使用 fc-match 获取最佳匹配的字体路径
            result = subprocess.run(
                ['fc-match', query, '--format=%{file}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                font_path = result.stdout.strip()
                if os.path.exists(font_path):
                    self._font_cache[cache_key] = font_path
                    self.logger.info(f"字体匹配成功: {query} -> {font_path}")
                    return font_path
            
        except Exception as e:
            self.logger.debug(f"fc-match查询失败 {font_family}: {e}")
        
        # 方法3: 回退到预定义路径映射
        font_path = self._get_font_path_fallback(font_family, weight)
        self._font_cache[cache_key] = font_path
        return font_path
    
    def _get_font_path_from_config(self, font_family: str, weight: str) -> Optional[str]:
        """从配置文件获取字体路径 - 环境无关"""
        try:
            import json
            
            # 查找字体配置文件
            config_paths = [
                os.path.join(os.path.dirname(__file__), "..", "fonts", "font_config.json"),
                os.path.join(os.path.dirname(__file__), "font_config.json"),
                "./fonts/font_config.json"
            ]
            
            for config_path in config_paths:
                if not os.path.exists(config_path):
                    continue
                    
                with open(config_path, 'r', encoding='utf-8') as f:
                    font_config = json.load(f)
                
                # 搜索字体文件
                for search_path in font_config.get('search_paths', []):
                    # 支持相对路径
                    if search_path.startswith('./'):
                        search_path = os.path.join(os.path.dirname(__file__), "..", search_path[2:])
                    
                    if not os.path.exists(search_path):
                        continue
                        
                    # 构建期望的文件名
                    if font_family in font_config.get('fonts', {}):
                        font_info = font_config['fonts'][font_family]
                        expected_file = font_info.get(weight, font_info.get('regular'))
                        
                        if expected_file:
                            font_path = os.path.join(search_path, expected_file)
                            if os.path.exists(font_path):
                                self.logger.info(f"配置文件匹配: {font_family} ({weight}) -> {font_path}")
                                return font_path
                        
                        # 尝试回退字体
                        for fallback in font_info.get('fallbacks', []):
                            if fallback in font_config.get('fonts', {}):
                                fallback_info = font_config['fonts'][fallback]
                                fallback_file = fallback_info.get(weight, fallback_info.get('regular'))
                                if fallback_file:
                                    font_path = os.path.join(search_path, fallback_file)
                                    if os.path.exists(font_path):
                                        self.logger.info(f"配置回退匹配: {fallback} -> {font_path}")
                                        return font_path
                
                break  # 只使用第一个找到的配置文件
                                        
        except Exception as e:
            self.logger.debug(f"从配置文件获取字体路径失败: {e}")
        
        return None
    
    def _get_font_path_fallback(self, font_family: str, weight: str = 'regular') -> str:
        """回退字体路径映射"""
        # 改进的字体路径映射，支持不同字体粗细
        font_paths = {
            # 无衬线字体
            "Arial": {
                "regular": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "bold": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "fallback": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            },
            "Helvetica": {
                "regular": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 
                "bold": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "fallback": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            },
            "DejaVu Sans": {
                "regular": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "fallback": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            },
            "Liberation Sans": {
                "regular": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "bold": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 
                "fallback": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            },
            "Ubuntu": {
                "regular": "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
                "bold": "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
                "fallback": "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
            },
            
            # 衬线字体
            "Times New Roman": {
                "regular": "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
                "bold": "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
                "fallback": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            },
            "Times": {
                "regular": "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
                "bold": "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
                "fallback": "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            },
            "DejaVu Serif": {
                "regular": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
                "bold": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
                "fallback": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            },
            "Liberation Serif": {
                "regular": "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
                "bold": "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
                "fallback": "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            },
            
            # 等宽字体
            "Courier New": {
                "regular": "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
                "bold": "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
                "fallback": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            },
            "DejaVu Sans Mono": {
                "regular": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 
                "bold": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
                "fallback": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            },
            "Liberation Mono": {
                "regular": "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
                "bold": "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
                "fallback": "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            },
            
            # 粗体/显示字体
            "Impact": {
                "regular": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Impact本身就是粗体
                "bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "fallback": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            },
            
            # 中文字体
            "WenQuanYi Zen Hei": {
                "regular": "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
                "bold": "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # 中文字体通常只有一个文件
                "fallback": "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            },
            "WenQuanYi Micro Hei": {
                "regular": "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                "bold": "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                "fallback": "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            },
            "Noto Sans CJK SC": {
                "regular": "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "bold": "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
                "fallback": "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            },
            "Noto Serif CJK SC": {
                "regular": "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
                "bold": "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
                "fallback": "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
            },
            
            # Lato 字体
            "Lato": {
                "regular": "/usr/share/fonts/truetype/lato/Lato-Regular.ttf",
                "bold": "/usr/share/fonts/truetype/lato/Lato-Bold.ttf",
                "light": "/usr/share/fonts/truetype/lato/Lato-Light.ttf",
                "fallback": "/usr/share/fonts/truetype/lato/Lato-Regular.ttf",
            }
        }
        
        # 首先尝试指定字体的路径
        if font_family in font_paths:
            font_config = font_paths[font_family]
            # 先尝试指定的weight
            if weight in font_config and os.path.exists(font_config[weight]):
                return font_config[weight]
            # 然后尝试fallback
            if "fallback" in font_config and os.path.exists(font_config["fallback"]):
                return font_config["fallback"]
            # 最后尝试regular
            if "regular" in font_config and os.path.exists(font_config["regular"]):
                return font_config["regular"]
        
        # 通用回退策略 - 按字体类型选择不同的默认字体
        fallback_order = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",          # 无衬线
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",         # 衬线
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",      # 等宽
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",             # 中文
            "/usr/share/fonts/truetype/lato/Lato-Regular.ttf",          # Lato
        ]
        
        for font_path in fallback_order:
            if os.path.exists(font_path):
                return font_path
        
        # 最后的回退
        return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    
    def validate_font(self, font_family: str) -> bool:
        """
        验证字体是否可用且能正常渲染
        
        Args:
            font_family: 字体族名称
            
        Returns:
            字体是否可用
        """
        if font_family in self.font_validation_cache:
            return self.font_validation_cache[font_family]
        
        try:
            font_path = self.get_font_path(font_family)
            
            if not os.path.exists(font_path):
                self.font_validation_cache[font_family] = False
                return False
            
            # 尝试使用PIL加载字体进行验证
            try:
                font = ImageFont.truetype(font_path, 20)
                # 创建测试图像并尝试渲染文本
                img = Image.new('RGB', (100, 50), 'white')
                draw = ImageDraw.Draw(img)
                draw.text((10, 10), 'Test', font=font, fill='black')
                
                self.font_validation_cache[font_family] = True
                return True
                
            except Exception as e:
                self.logger.warning(f"字体 {font_family} 无法正常渲染: {e}")
                self.font_validation_cache[font_family] = False
                return False
                
        except Exception as e:
            self.logger.error(f"验证字体 {font_family} 时发生错误: {e}")
            self.font_validation_cache[font_family] = False
            return False
    
    def get_font_info(self, font_family: str) -> Dict[str, any]:
        """
        获取字体详细信息
        
        Args:
            font_family: 字体族名称
            
        Returns:
            字体信息字典
        """
        font_path = self.get_font_path(font_family)
        
        info = {
            'name': font_family,
            'path': font_path,
            'exists': os.path.exists(font_path),
            'size': 0,
            'type': 'unknown'
        }
        
        if info['exists']:
            try:
                # 获取文件大小
                info['size'] = os.path.getsize(font_path)
                
                # 判断字体类型
                if 'serif' in font_path.lower() or font_family.lower() in ['times', 'georgia', 'palatino']:
                    info['type'] = 'serif'
                elif 'mono' in font_path.lower() or font_family.lower() in ['courier', 'consolas', 'monaco']:
                    info['type'] = 'monospace'
                elif 'bold' in font_path.lower() or font_family.lower() in ['impact', 'arial black']:
                    info['type'] = 'display'
                else:
                    info['type'] = 'sans-serif'
                    
            except Exception as e:
                self.logger.warning(f"获取字体信息失败 {font_family}: {e}")
        
        return info
    
    def install_common_fonts(self) -> bool:
        """
        安装常用字体包
        
        Returns:
            安装是否成功
        """
        try:
            # 要安装的字体包列表
            font_packages = [
                'fonts-liberation',      # Liberation 字体 (Arial, Times, Courier 替代)
                'fonts-dejavu-core',     # DejaVu 字体
                'fonts-noto-core',       # Noto 字体
                'fonts-ubuntu',          # Ubuntu 字体
                'fonts-cascadia-code',   # Cascadia Code 等宽字体
                'fonts-firacode',        # Fira Code 等宽字体
                'ttf-mscorefonts-installer',  # 微软核心字体
            ]
            
            self.logger.info("开始安装常用字体包...")
            
            # 更新包列表
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            
            # 安装字体包
            for package in font_packages:
                try:
                    result = subprocess.run(
                        ['sudo', 'apt', 'install', '-y', package],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if result.returncode == 0:
                        self.logger.info(f"成功安装字体包: {package}")
                    else:
                        self.logger.warning(f"安装字体包失败 {package}: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"安装字体包超时: {package}")
                except Exception as e:
                    self.logger.warning(f"安装字体包异常 {package}: {e}")
            
            # 刷新字体缓存
            subprocess.run(['fc-cache', '-f', '-v'], timeout=60)
            
            # 清除缓存，重新检测字体
            self._available_fonts = None
            self._font_cache.clear()
            self.font_validation_cache.clear()
            
            self.logger.info("字体安装完成，重新检测可用字体...")
            new_fonts = self.get_available_fonts()
            self.logger.info(f"安装后检测到 {len(new_fonts)} 种可用字体")
            
            return True
            
        except Exception as e:
            self.logger.error(f"安装字体时发生错误: {e}")
            return False
    
    def generate_font_preview(self, font_family: str, output_path: str, 
                            text: str = "Hello World 你好世界", size: int = 24) -> bool:
        """
        生成字体预览图
        
        Args:
            font_family: 字体族名称
            output_path: 输出图像路径
            text: 预览文本
            size: 字体大小
            
        Returns:
            生成是否成功
        """
        try:
            font_path = self.get_font_path(font_family)
            
            if not os.path.exists(font_path):
                self.logger.error(f"字体文件不存在: {font_path}")
                return False
            
            # 创建预览图
            img_width, img_height = 400, 100
            img = Image.new('RGB', (img_width, img_height), 'white')
            draw = ImageDraw.Draw(img)
            
            # 加载字体
            font = ImageFont.truetype(font_path, size)
            
            # 计算文本位置（居中）
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (img_width - text_width) // 2
            y = (img_height - text_height) // 2
            
            # 绘制文本
            draw.text((x, y), text, font=font, fill='black')
            
            # 添加字体名称标签
            label_font = ImageFont.load_default()
            draw.text((10, 10), f"Font: {font_family}", font=label_font, fill='gray')
            draw.text((10, img_height - 20), f"Path: {os.path.basename(font_path)}", 
                     font=label_font, fill='gray')
            
            # 保存图像
            img.save(output_path)
            self.logger.info(f"字体预览图已保存: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"生成字体预览图失败 {font_family}: {e}")
            return False


# 全局字体管理器实例
_font_manager = None

def get_font_manager() -> FontManager:
    """获取全局字体管理器实例"""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager