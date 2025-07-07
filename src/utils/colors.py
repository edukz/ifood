#!/usr/bin/env python3
"""
Sistema de cores para output do terminal
Melhora a visualização durante o processo de scraping
"""

import sys
from typing import Optional


class Colors:
    """Classe com códigos de cores ANSI para terminal"""
    
    # Reset
    RESET = '\033[0m'
    
    # Cores básicas
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Cores brilhantes
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Estilos
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKETHROUGH = '\033[9m'
    
    # Backgrounds
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Ícones úteis (Unicode)
    CHECK = '✓'
    CROSS = '✗'
    ARROW = '→'
    BULLET = '•'
    STAR = '★'
    INFO = 'ℹ'
    WARNING = '⚠'
    ERROR = '✖'
    ROCKET = '🚀'
    CLOCK = '⏱'
    FOLDER = '📁'
    FILE = '📄'
    SEARCH = '🔍'
    DOWNLOAD = '⬇'
    UPLOAD = '⬆'
    SYNC = '🔄'
    
    @staticmethod
    def is_supported():
        """Verifica se o terminal suporta cores"""
        # Windows terminal moderno suporta cores ANSI
        if sys.platform == 'win32':
            return True
        # Unix/Linux geralmente suportam
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


class ColorPrinter:
    """Classe utilitária para imprimir texto colorido"""
    
    def __init__(self, use_colors: bool = None):
        """
        Inicializa o ColorPrinter
        
        Args:
            use_colors: Forçar uso de cores (None = auto-detectar)
        """
        if use_colors is None:
            self.use_colors = Colors.is_supported()
        else:
            self.use_colors = use_colors
    
    def _colorize(self, text: str, color: str, style: str = '') -> str:
        """Aplica cor ao texto se suportado"""
        if not self.use_colors:
            return text
        return f"{style}{color}{text}{Colors.RESET}"
    
    # Métodos de conveniência para cores comuns
    def success(self, text: str, bold: bool = False) -> str:
        """Texto verde para sucesso"""
        style = Colors.BOLD if bold else ''
        return self._colorize(text, Colors.GREEN, style)
    
    def error(self, text: str, bold: bool = True) -> str:
        """Texto vermelho para erro"""
        style = Colors.BOLD if bold else ''
        return self._colorize(text, Colors.RED, style)
    
    def warning(self, text: str, bold: bool = False) -> str:
        """Texto amarelo para aviso"""
        style = Colors.BOLD if bold else ''
        return self._colorize(text, Colors.YELLOW, style)
    
    def info(self, text: str, bold: bool = False) -> str:
        """Texto azul para informação"""
        style = Colors.BOLD if bold else ''
        return self._colorize(text, Colors.BLUE, style)
    
    def highlight(self, text: str, bold: bool = True) -> str:
        """Texto ciano para destaque"""
        style = Colors.BOLD if bold else ''
        return self._colorize(text, Colors.CYAN, style)
    
    def dim(self, text: str) -> str:
        """Texto apagado para informação secundária"""
        return self._colorize(text, Colors.BRIGHT_BLACK)
    
    def progress(self, text: str) -> str:
        """Texto magenta para progresso"""
        return self._colorize(text, Colors.MAGENTA)
    
    # Métodos para ações específicas do scraping
    def action(self, action: str, description: str) -> str:
        """Formata uma ação do scraping"""
        action_colored = self._colorize(f"[{action}]", Colors.BRIGHT_CYAN, Colors.BOLD)
        return f"{action_colored} {description}"
    
    def category(self, name: str, count: Optional[int] = None) -> str:
        """Formata nome de categoria"""
        cat_text = self._colorize(name, Colors.BRIGHT_MAGENTA, Colors.BOLD)
        if count is not None:
            count_text = self.dim(f"({count} items)")
            return f"{cat_text} {count_text}"
        return cat_text
    
    def restaurant(self, name: str, rating: Optional[float] = None) -> str:
        """Formata nome de restaurante"""
        rest_text = self._colorize(name, Colors.BRIGHT_YELLOW)
        if rating is not None:
            if rating >= 4.5:
                rating_color = Colors.BRIGHT_GREEN
            elif rating >= 4.0:
                rating_color = Colors.GREEN
            elif rating >= 3.5:
                rating_color = Colors.YELLOW
            else:
                rating_color = Colors.RED
            rating_text = self._colorize(f"{rating:.1f}★", rating_color)
            return f"{rest_text} {rating_text}"
        return rest_text
    
    def stats(self, label: str, value: str, good: bool = True) -> str:
        """Formata estatística"""
        label_colored = self.dim(f"{label}:")
        if good:
            value_colored = self.success(value, bold=True)
        else:
            value_colored = self.warning(value, bold=True)
        return f"{label_colored} {value_colored}"
    
    def phase(self, phase_name: str, step: int = None, total: int = None) -> str:
        """Formata fase do processo"""
        phase_text = self._colorize(f"◆ {phase_name}", Colors.BRIGHT_BLUE, Colors.BOLD)
        if step and total:
            progress = self.dim(f"[{step}/{total}]")
            return f"{phase_text} {progress}"
        return phase_text
    
    def url(self, url: str) -> str:
        """Formata URL"""
        return self._colorize(url, Colors.BLUE, Colors.UNDERLINE)
    
    def file_path(self, path: str) -> str:
        """Formata caminho de arquivo"""
        return self._colorize(path, Colors.CYAN)
    
    # Métodos para barras de progresso
    def progress_bar(self, current: int, total: int, width: int = 50, 
                    filled_char: str = '█', empty_char: str = '░') -> str:
        """Cria uma barra de progresso colorida"""
        if total == 0:
            percent = 0
        else:
            percent = current / total
        
        filled_width = int(width * percent)
        empty_width = width - filled_width
        
        # Cor baseada no progresso
        if percent >= 0.9:
            bar_color = Colors.BRIGHT_GREEN
        elif percent >= 0.7:
            bar_color = Colors.GREEN
        elif percent >= 0.5:
            bar_color = Colors.YELLOW
        elif percent >= 0.3:
            bar_color = Colors.BRIGHT_YELLOW
        else:
            bar_color = Colors.RED
        
        filled_part = self._colorize(filled_char * filled_width, bar_color)
        empty_part = self.dim(empty_char * empty_width)
        percent_text = self._colorize(f"{percent*100:.1f}%", bar_color, Colors.BOLD)
        
        return f"[{filled_part}{empty_part}] {percent_text}"
    
    def spinner_frame(self, frame: int) -> str:
        """Retorna um frame do spinner animado"""
        frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        return self._colorize(frames[frame % len(frames)], Colors.BRIGHT_CYAN)


# Instância global para uso fácil
color_printer = ColorPrinter()


# Funções de conveniência
def print_success(text: str, bold: bool = False):
    """Imprime mensagem de sucesso"""
    print(color_printer.success(f"{Colors.CHECK} {text}", bold))


def print_error(text: str, bold: bool = True):
    """Imprime mensagem de erro"""
    print(color_printer.error(f"{Colors.ERROR} {text}", bold))


def print_warning(text: str, bold: bool = False):
    """Imprime mensagem de aviso"""
    print(color_printer.warning(f"{Colors.WARNING} {text}", bold))


def print_info(text: str, bold: bool = False):
    """Imprime mensagem informativa"""
    print(color_printer.info(f"{Colors.INFO} {text}", bold))


def print_action(action: str, description: str):
    """Imprime uma ação sendo executada"""
    print(color_printer.action(action, description))


def print_phase(phase_name: str, step: int = None, total: int = None):
    """Imprime fase do processo"""
    print(color_printer.phase(phase_name, step, total))


def print_progress(current: int, total: int, label: str = "Progress"):
    """Imprime barra de progresso"""
    bar = color_printer.progress_bar(current, total)
    label_colored = color_printer.dim(label)
    print(f"\r{label_colored} {bar}", end='', flush=True)
    if current >= total:
        print()  # Nova linha ao completar


# Exemplo de uso
if __name__ == "__main__":
    # Teste das cores
    print("\n=== TESTE DE CORES ===\n")
    
    cp = ColorPrinter()
    
    print_phase("Iniciando Scraping")
    print_action("NAVEGANDO", "Acessando página de categorias")
    print_info("16 categorias encontradas")
    
    print("\nCategorias:")
    print("  " + cp.category("Pizza", 47))
    print("  " + cp.category("Lanches", 133))
    print("  " + cp.category("Brasileira", 163))
    
    print("\nRestaurantes encontrados:")
    print("  " + cp.restaurant("Pizzaria Bella Itália", 4.8))
    print("  " + cp.restaurant("Burger King", 4.2))
    print("  " + cp.restaurant("Subway", 3.9))
    
    print("\nEstatísticas:")
    print("  " + cp.stats("Novos", "535", good=True))
    print("  " + cp.stats("Atualizados", "523", good=True))
    print("  " + cp.stats("Falhas", "2", good=False))
    
    print("\nProgresso:")
    for i in range(0, 101, 10):
        print_progress(i, 100, "Extraindo")
        import time
        time.sleep(0.1)
    
    print_success("Extração concluída com sucesso!")
    print_warning("Alguns restaurantes podem estar duplicados")
    print_error("2 restaurantes falharam na extração")