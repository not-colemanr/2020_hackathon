import math, random, pygame
from pygame.locals import (
    RLEACCEL,
    K_w,
    K_a,
    K_s,
    K_d,
    K_ESCAPE,
    KEYDOWN,
    QUIT
)

pygame.init()
myfont = pygame.font.SysFont('freesansbold.ttf', 30)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS_CAP = 30
BOSS_HEALTH_MAX = 50
BOSS_HEALTH_WIDTH = min(300, SCREEN_WIDTH//2)
BOSS_HEALTH_POSITIONX = (SCREEN_WIDTH - BOSS_HEALTH_WIDTH) // 2
LAVA_FREQUENCY = 1000 # in milliseconds

class Player(pygame.sprite.Sprite):

    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.Surface((25, 25))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        self.health = 5
        self.invulnerableTimer = 0
        self.shootTimer = 0
        self.clock = pygame.time.Clock()
        self.alive = True

    def update(self, pressed_keys):
        if self.alive:
            # move based on WASD input
            if pressed_keys[K_w]:
                self.rect.move_ip(0, -5)
            if pressed_keys[K_s]:
                self.rect.move_ip(0, 5)
            if pressed_keys[K_a]:
                self.rect.move_ip(-5, 0)
            if pressed_keys[K_d]:
                self.rect.move_ip(5, 0)

            # don't move outside the screen
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
            if self.rect.top <= 0:
                self.rect.top = 0
            if self.rect.bottom >= SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT

            #time in milliseconds since we were last here
            dt = self.clock.tick()

            if self.invulnerableTimer > 0:
                self.invulnerableTimer -= dt

                # flashing effect
                roundedTimer = self.invulnerableTimer // 100
                if roundedTimer in [9,7,5,3,1]:
                    self.surf.fill((50,50,50))
                else:
                    self.surf.fill((255,255,255))
            
            if self.shootTimer > 0:
                self.shootTimer -= dt

    def takeDamage(self):
        if self.alive:
            if self.invulnerableTimer <= 0:
                self.health -= 1
                self.invulnerableTimer = 1000
                print("hurt, health is now ", self.health)
                if self.health == 0:
                    self.alive = False
                    self.kill()

    def shoot(self):
        if self.alive:
            if self.shootTimer <= 0:
                target = list(pygame.mouse.get_pos())
                # adjust for using the player as origin
                target[0] -= self.rect.centerx - (self.surf.get_width()//2)
                target[1] -= self.rect.centery - (self.surf.get_height()//2)
                # get hypotenuse and use that to calculate normalized vector
                radius = math.sqrt(math.pow(target[0], 2) + math.pow(target[1], 2))
                target = (target[0] / radius, target[1] / radius)
                new_Bullet = Bullet((self.rect.centerx + (self.surf.get_width()//2), self.rect.centery), target)
                
                self.shootTimer = 500
                return new_Bullet

    def getPosition(self):
        return [self.rect[0], self.rect[1]]

class Bullet(pygame.sprite.Sprite):
    def __init__(self, location, target):
        super(Bullet, self).__init__()
        self.surf = pygame.Surface((10, 10))
        self.surf.fill((0, 220, 220))
        self.rect = self.surf.get_rect(center=location)
        self.speed = 10
        self.direction = target

    def update(self):
        self.rect.move_ip(int(self.direction[0] * self.speed), int(self.direction[1] * self.speed))

        # if the object is completely outside of the screen, remove it
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Volcano(pygame.sprite.Sprite):
    def __init__(self):
        super(Volcano, self).__init__()
        self.surf = pygame.image.load("images/Volcano.png").convert()
        self.surf.set_colorkey((255,255,255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(
                SCREEN_WIDTH//2,
                SCREEN_HEIGHT//2
            )
        )
        self.healthMax = BOSS_HEALTH_MAX
        self.health = self.healthMax
        self.alive = True

    def throwLava(self, target=None):
        if self.alive:
            if target:
                # adjust for using the center of screen as origin
                target[0] -= SCREEN_WIDTH/2
                target[1] -= SCREEN_HEIGHT/2

                # add some deviation to shots
                target[0] += random.uniform(-SCREEN_WIDTH/5, SCREEN_WIDTH/4)
                target[1] += random.uniform(-SCREEN_HEIGHT/5, SCREEN_HEIGHT/4)

                # get hypotenuse and use that to calculate normalized vector
                radius = math.sqrt(math.pow(target[0], 2) + math.pow(target[1], 2))
                target = (target[0] / radius, target[1] / radius)
            else:
                # generate a vector by picking a random point on a circle and doing math
                angle = random.uniform(0, 2 * math.pi)
                target = (math.cos(angle), math.sin(angle))
            new_Rock = LavaRock((self.rect.centerx, self.rect.centery), target)
            return new_Rock

    def takeDamage(self):
        if self.alive:
            self.health -= 1
            if self.health == 0:
                self.alive = False
                self.surf = pygame.image.load("images/Mountain.png").convert()
                self.surf.set_colorkey((255,255,255), RLEACCEL)

class LavaRock(pygame.sprite.Sprite):
    def __init__(self, location, target):
        super(LavaRock, self).__init__()
        self.surf = pygame.Surface((25, 25))
        self.surf.fill((200, 100, 0))
        self.rect = self.surf.get_rect(center=location)
        self.speed = random.uniform(9, 10)
        self.direction = target

    def update(self):
        self.rect.move_ip(int(self.direction[0] * self.speed), int(self.direction[1] * self.speed))

        # if the object is completely outside of the screen, remove it
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

def main():

    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    clock = pygame.time.Clock()

    THROWLAVA = pygame.USEREVENT + 1
    pygame.time.set_timer(THROWLAVA, LAVA_FREQUENCY)

    player = Player()
    volcano = Volcano()

    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()

    all_sprites.add(player)
    all_sprites.add(volcano)

    running = True

    print("Welcome!\nMove with WASD, aim with the mouse, and left click to shoot.\nPress Escape to exit.")

    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    print("Quit by escape key")
                    running = False
            elif event.type == THROWLAVA:
                # throw 5 lava rocks targetting the player
                for i in range(0, 5):
                    new_rock = volcano.throwLava(player.getPosition())
                    if new_rock:
                        enemies.add(new_rock)
                        all_sprites.add(new_rock)
            elif event.type == QUIT:
                print("Quit by generic quit event")
                running = False

        pressed_keys = pygame.key.get_pressed()
        pressed_mouse = pygame.mouse.get_pressed()
        player.update(pressed_keys)

        if pressed_mouse[0]:
            new_Bullet = player.shoot()
            if new_Bullet:
                all_sprites.add(new_Bullet)
                projectiles.add(new_Bullet)

        projectiles.update()

        enemies.update()

        screen.fill((0, 0, 0))

        # Volcano health bar
        pygame.draw.rect(screen, (200, 0, 0), (BOSS_HEALTH_POSITIONX, SCREEN_HEIGHT-30, round(BOSS_HEALTH_WIDTH * (volcano.health / volcano.healthMax)), 30))

        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

        if pygame.sprite.spritecollideany(player, enemies):
            player.takeDamage()

        for projectile in pygame.sprite.spritecollide(volcano, projectiles, 1):
            volcano.takeDamage()

        if not volcano.alive:
            text = myfont.render('You did it, Mount Shasta is cool again!', False, (255, 255, 255))
            textRect = text.get_rect()
            textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 8)
            screen.blit(text, textRect)
        elif not player.alive:
            text = myfont.render('You have died. Now we are all doomed.', False, (255, 255, 255))
            textRect = text.get_rect()
            textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 8)
            screen.blit(text, textRect)

        pygame.display.flip()

        # cap FPS
        clock.tick(FPS_CAP)

if __name__=="__main__":
   main()