import pygame
from ui import UiBrain, EventManager
import time

pygame.init()

ui = UiBrain()

em = EventManager(ui)

clock = pygame.time.Clock()

while True:

    start = time.time()

    ui.update_background()

    em.manage_events(pygame.event.get())

    ui.mainloop()

    print(f"{1 / (time.time() - start):.2f}")
