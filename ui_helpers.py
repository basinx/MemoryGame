import pygame

# UI Helper Functions
def draw_text(surface, text, pos, font, color=(255, 255, 255)):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def draw_wrapped_text(surface, text, pos, font, color=(255, 255, 255), max_width=700):
    words = text.split(' ')
    lines = []
    current_line = ''

    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + ' '
    lines.append(current_line)

    x, y = pos
    for line in lines:
        line_surface = font.render(line, True, color)
        surface.blit(line_surface, (x, y))
        y += font.get_height()


def button(rect, text, screen, font):
    pygame.draw.rect(screen, (0, 128, 255), rect)
    draw_text(screen, text, (rect[0] + 10, rect[1] + 10), font)
    return rect

# Text input box class with auto-overwrite on click.
class TextInputBox:
    def __init__(self, x, y, w, h, text='', font=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = (200, 200, 200)
        self.color_active = (255, 255, 255)
        self.color = self.color_inactive
        self.text = text
        self.font = font
        self.txt_surface = font.render(text, True, (0, 0, 0)) if font else None
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.text = ""
                self.txt_surface = self.font.render(self.text, True, (0, 0, 0))
                self.color = self.color_active
            else:
                self.active = False
                self.color = self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.color = self.color_inactive
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = self.font.render(self.text, True, (0, 0, 0))

    def draw(self, surface):
        bg_color = (150, 150, 150) if self.active else (200, 200, 200)
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, self.color, self.rect, 2)
        surface.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

