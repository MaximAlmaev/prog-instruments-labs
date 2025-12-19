
import random 
import sys 
import pygame 
import logging
import os
from pygame.locals import *
from datetime import datetime

# Настройка логирования
def setup_logging():
    """Настройка системы логирования"""
    # Создаем папку для логов если ее нет
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Формат времени для имени файла
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f'logs/flappy_bird_{timestamp}.log'
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Также выводим в консоль
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Логирование запущено. Файл лога: {log_filename}")
    return logger

# Инициализация логирования
logger = setup_logging()

# Все игровые переменные
window_width = 600
window_height = 499

# set height and width of window 
window = pygame.display.set_mode((window_width, window_height)) 
elevation = window_height * 0.8
game_images = {} 
framepersecond = 32
pipeimage = 'images/pipe.png'
background_image = 'images/background.jpg'
birdplayer_image = 'images/bird.png'
sealevel_image = 'images/base.jfif'

def load_image_with_logging(path, image_name):
    """Загрузка изображения с логированием"""
    try:
        image = pygame.image.load(path).convert_alpha()
        logger.info(f"Изображение '{image_name}' загружено успешно: {path}")
        return image
    except Exception as e:
        logger.error(f"Ошибка загрузки изображения '{image_name}' ({path}): {e}")
        # Создаем заглушку
        surface = pygame.Surface((50, 50))
        surface.fill((255, 0, 255))  # Фиолетовый цвет для ошибки
        return surface

def flappygame(): 
    logger.info("=== НАЧАЛО НОВОЙ ИГРЫ ===")
    
    your_score = 0
    horizontal = int(window_width/5) 
    vertical = int(window_width/2) 
    ground = 0
    mytempheight = 100

    # Generating two pipes for blitting on window 
    first_pipe = createPipe() 
    second_pipe = createPipe() 
    
    logger.info(f"Созданы начальные трубы: 1:{first_pipe[0]['y']:.1f}, 2:{second_pipe[0]['y']:.1f}")

    # List containing lower pipes 
    down_pipes = [ 
        {'x': window_width+300-mytempheight, 
        'y': first_pipe[1]['y']}, 
        {'x': window_width+300-mytempheight+(window_width/2), 
        'y': second_pipe[1]['y']}, 
    ] 

    # List Containing upper pipes 
    up_pipes = [ 
        {'x': window_width+300-mytempheight, 
        'y': first_pipe[0]['y']}, 
        {'x': window_width+200-mytempheight+(window_width/2), 
        'y': second_pipe[0]['y']}, 
    ] 

    # pipe velocity along x 
    pipeVelX = -4

    # bird velocity 
    bird_velocity_y = -9
    bird_Max_Vel_Y = 10
    bird_Min_Vel_Y = -8
    birdAccY = 1

    bird_flap_velocity = -8
    bird_flapped = False
    frame_count = 0
    
    logger.info(f"Начальная позиция птицы: ({horizontal}, {vertical})")
    
    while True: 
        frame_count += 1
        
        for event in pygame.event.get(): 
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): 
                logger.info(f"Игра завершена. Итоговый счет: {your_score}")
                pygame.quit() 
                sys.exit() 
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP): 
                if vertical > 0: 
                    bird_velocity_y = bird_flap_velocity 
                    bird_flapped = True
                    logger.debug(f"Прыжок! Кадр: {frame_count}, Позиция Y: {vertical:.1f}")

        # This function will return true 
        # if the flappybird is crashed 
        game_over = isGameOver(horizontal, 
                            vertical, 
                            up_pipes, 
                            down_pipes) 
        if game_over: 
            logger.info(f"=== ИГРА ОКОНЧЕНА === Счет: {your_score}, Кадры: {frame_count}")
            # Логируем причину проигрыша
            if vertical > elevation - 25:
                logger.info("Причина: столкновение с землей")
            elif vertical < 0:
                logger.info("Причина: вылет за верхнюю границу")
            else:
                logger.info("Причина: столкновение с трубой")
            return

        # check for your_score 
        playerMidPos = horizontal + game_images['flappybird'].get_width()/2
        for pipe in up_pipes: 
            pipeMidPos = pipe['x'] + game_images['pipeimage'][0].get_width()/2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4: 
                your_score += 1
                logger.info(f"Счет увеличен: {your_score} (кадр: {frame_count})")

        if bird_velocity_y < bird_Max_Vel_Y and not bird_flapped: 
            bird_velocity_y += birdAccY 

        if bird_flapped: 
            bird_flapped = False
        playerHeight = game_images['flappybird'].get_height() 
        vertical = vertical + min(bird_velocity_y, elevation - vertical - playerHeight) 

        # move pipes to the left 
        for upperPipe, lowerPipe in zip(up_pipes, down_pipes): 
            upperPipe['x'] += pipeVelX 
            lowerPipe['x'] += pipeVelX 

        # Add a new pipe when the first is 
        # about to cross the leftmost part of the screen 
        if 0 < up_pipes[0]['x'] < 5: 
            newpipe = createPipe() 
            up_pipes.append(newpipe[0]) 
            down_pipes.append(newpipe[1]) 
            logger.debug(f"Создана новая труба на позиции {newpipe[0]['x']}")

        # if the pipe is out of the screen, remove it 
        if up_pipes[0]['x'] < -game_images['pipeimage'][0].get_width(): 
            up_pipes.pop(0) 
            down_pipes.pop(0) 
            logger.debug(f"Труба удалена. Осталось труб: {len(up_pipes)}")

        # Логируем состояние каждые 60 кадров
        if frame_count % 60 == 0:
            logger.debug(f"Статистика: Счет={your_score}, Птица=({horizontal:.1f}, {vertical:.1f}), "
                        f"Труб={len(up_pipes)}, Скорость={bird_velocity_y:.1f}")

        # Lets blit our game images now 
        window.blit(game_images['background'], (0, 0)) 
        for upperPipe, lowerPipe in zip(up_pipes, down_pipes): 
            window.blit(game_images['pipeimage'][0], 
                        (upperPipe['x'], upperPipe['y'])) 
            window.blit(game_images['pipeimage'][1], 
                        (lowerPipe['x'], lowerPipe['y'])) 

        window.blit(game_images['sea_level'], (ground, elevation)) 
        window.blit(game_images['flappybird'], (horizontal, vertical)) 

        # Fetching the digits of score. 
        numbers = [int(x) for x in list(str(your_score))] 
        width = 0

        # finding the width of score images from numbers. 
        for num in numbers: 
            width += game_images['scoreimages'][num].get_width() 
        Xoffset = (window_width - width)/1.1

        # Blitting the images on the window. 
        for num in numbers: 
            window.blit(game_images['scoreimages'][num], 
                        (Xoffset, window_width*0.02)) 
            Xoffset += game_images['scoreimages'][num].get_width() 

        # Refreshing the game window and displaying the score. 
        pygame.display.update() 
        framepersecond_clock.tick(framepersecond) 


def isGameOver(horizontal, vertical, up_pipes, down_pipes): 
    # Логируем проверку столкновений в режиме отладки
    if vertical > elevation - 25 or vertical < 0: 
        logger.debug(f"Столкновение с границей! Y={vertical:.1f}, Лимит={elevation-25}")
        return True

    for pipe in up_pipes: 
        pipeHeight = game_images['pipeimage'][0].get_height() 
        if(vertical < pipeHeight + pipe['y'] and abs(horizontal - pipe['x']) < game_images['pipeimage'][0].get_width()): 
            logger.debug(f"Столкновение с верхней трубой! X={horizontal:.1f}, Труба X={pipe['x']:.1f}")
            return True

    for pipe in down_pipes: 
        if (vertical + game_images['flappybird'].get_height() > pipe['y']) and abs(horizontal - pipe['x']) < game_images['pipeimage'][0].get_width(): 
            logger.debug(f"Столкновение с нижней трубой! X={horizontal:.1f}, Труба X={pipe['x']:.1f}")
            return True
    return False


def createPipe(): 
    offset = window_height/3
    pipeHeight = game_images['pipeimage'][0].get_height() 
    y2 = offset + random.randrange( 
            0, int(window_height - game_images['sea_level'].get_height() - 1.2 * offset)) 
    pipeX = window_width + 10
    y1 = pipeHeight - y2 + offset 
    pipe = [ 
        # upper Pipe 
        {'x': pipeX, 'y': -y1}, 

        # lower Pipe 
        {'x': pipeX, 'y': y2} 
    ] 
    return pipe 


# program where the game starts 
if __name__ == "__main__": 
    logger.info("=" * 50)
    logger.info("ЗАПУСК ИГРЫ FLAPPY BIRD")
    logger.info("=" * 50)

    # For initializing modules of pygame library 
    try:
        pygame.init() 
        logger.info("PyGame инициализирован успешно")
    except Exception as e:
        logger.critical(f"Ошибка инициализации PyGame: {e}")
        sys.exit(1)
        
    framepersecond_clock = pygame.time.Clock() 

    # Sets the title on top of game window 
    pygame.display.set_caption('Flappy Bird Game') 

    # Load all the images which we will use in the game 
    logger.info("Начинаю загрузку изображений...")

    # images for displaying score 
    game_images['scoreimages'] = ( 
        load_image_with_logging('images/0.png', 'цифра 0'),
        load_image_with_logging('images/1.png', 'цифра 1'),
        load_image_with_logging('images/2.png', 'цифра 2'),
        load_image_with_logging('images/3.png', 'цифра 3'),
        load_image_with_logging('images/4.png', 'цифра 4'),
        load_image_with_logging('images/5.png', 'цифра 5'),
        load_image_with_logging('images/6.png', 'цифра 6'),
        load_image_with_logging('images/7.png', 'цифра 7'),
        load_image_with_logging('images/8.png', 'цифра 8'),
        load_image_with_logging('images/9.png', 'цифра 9')
    ) 
    
    game_images['flappybird'] = load_image_with_logging(
        birdplayer_image, 'птица'
    )
    game_images['sea_level'] = load_image_with_logging(
        sealevel_image, 'земля'
    )
    game_images['background'] = load_image_with_logging(
        background_image, 'фон'
    )
    
    # Загружаем трубу и создаем верхнюю и нижнюю версии
    pipe_img = load_image_with_logging(pipeimage, 'труба')
    game_images['pipeimage'] = (
        pygame.transform.rotate(pipe_img, 180), 
        pipe_img
    )
    
    logger.info(f"Все изображения загружены. Размер птицы: {game_images['flappybird'].get_size()}")
    logger.info(f"Размер окна: {window_width}x{window_height}")
    logger.info(f"FPS: {framepersecond}")

    print("WELCOME TO THE FLAPPY BIRD GAME") 
    print("Press space or enter to start the game") 

    # Here starts the main game 
    logger.info("Игра готова к запуску. Ожидание начала...")

    while True: 
        # sets the coordinates of flappy bird 
        horizontal = int(window_width/5) 
        vertical = int( 
            (window_height - game_images['flappybird'].get_height())/2) 
        ground = 0
        
        logger.debug("Главное меню: ожидание ввода пользователя")
        
        while True: 
            for event in pygame.event.get(): 
                # if user clicks on cross button, close the game 
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): 
                    logger.info("Игра завершена пользователем из главного меню")
                    pygame.quit() 
                    sys.exit() 

                # If the user presses space or up key, start the game for them 
                elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP): 
                    logger.info("Пользователь начал игру (пробел/стрелка вверх)")
                    flappygame() 
                    logger.info("Возврат в главное меню")
                    # После завершения игры перерисовываем главное меню

                # if user doesn't press anykey Nothing happen 
                else: 
                    window.blit(game_images['background'], (0, 0)) 
                    window.blit(game_images['flappybird'], 
                                (horizontal, vertical)) 
                    window.blit(game_images['sea_level'], (ground, elevation)) 
                    
                    # Добавляем текст в главном меню
                    font = pygame.font.SysFont(None, 36)
                    text = font.render("Press SPACE to start", True, (255, 255, 255))
                    text_rect = text.get_rect(center=(window_width//2, window_height//4))
                    window.blit(text, text_rect)
                    
                    pygame.display.update() 
                    framepersecond_clock.tick(framepersecond)
