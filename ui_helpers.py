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
        # render text surface only if font provided
        self.txt_surface = font.render(text, True, (0, 0, 0)) if font else None
        self.active = False
        # new: error state for validation (e.g., missing question file)
        self.error = False
        self.error_color = (255, 0, 0)

        # Backspace repeat configuration/state
        # initial delay before repeating (ms) and repeat interval (ms)
        self.initial_backspace_delay_ms = 700
        self.backspace_repeat_interval_ms = 50
        self._backspace_held = False
        self._backspace_start_ticks = 0
        self._backspace_last_repeat_ticks = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                # clicking activates and clears the current text
                self.active = True
                self.text = ""
                self.txt_surface = self.font.render(self.text, True, (0, 0, 0))
                self.color = self.color_active
                # clear any prior error when user clicks to edit
                self.error = False
            else:
                self.active = False
                self.color = self.color_inactive
        # Key events while active
        if self.active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = self.color_inactive
                elif event.key == pygame.K_BACKSPACE:
                    # immediate delete on keydown
                    self.text = self.text[:-1]
                    # start held-state timing for repeat
                    self._backspace_held = True
                    self._backspace_start_ticks = pygame.time.get_ticks()
                    self._backspace_last_repeat_ticks = self._backspace_start_ticks
                else:
                    self.text += event.unicode
                # update rendered surface
                self.txt_surface = self.font.render(self.text, True, (0, 0, 0))
            elif event.type == pygame.KEYUP:
                # stop repeating when backspace released
                if event.key == pygame.K_BACKSPACE:
                    self._backspace_held = False
                    self._backspace_start_ticks = 0
                    self._backspace_last_repeat_ticks = 0

    def update(self):
        """Call once per frame to handle repeating backspace while held.
        This method is a no-op if the box is not active or backspace isn't held.
        """
        if not self.active:
            return
        if self._backspace_held and self.text:
            now = pygame.time.get_ticks()
            elapsed = now - self._backspace_start_ticks
            if elapsed >= self.initial_backspace_delay_ms:
                # enough time passed to start repeating
                if now - self._backspace_last_repeat_ticks >= self.backspace_repeat_interval_ms:
                    # delete one char and advance last repeat time
                    self.text = self.text[:-1]
                    self._backspace_last_repeat_ticks = now
                    # update rendered surface
                    self.txt_surface = self.font.render(self.text, True, (0, 0, 0))

    def draw(self, surface):
        # background color slightly different when active
        bg_color = (150, 150, 150) if self.active else (200, 200, 200)
        # if error, tint background slightly and draw red border
        if self.error:
            bg_color = (255, 220, 220)
            border_color = self.error_color
        else:
            border_color = self.color
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 2)
        # ensure txt_surface exists to avoid crashes
        if not self.txt_surface and self.font:
            self.txt_surface = self.font.render(self.text, True, (0, 0, 0))
        surface.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

    def set_error(self, val=True):
        self.error = val
