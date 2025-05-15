import pygame
import random
import math

pygame.init()
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
SPAWN_ENEMY = pygame.USEREVENT + 1
SPAWN_MINI = pygame.USEREVENT + 2

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

background = pygame.transform.scale(pygame.image.load("assets/background.png"), (WIDTH, HEIGHT))

#Class Bullet
class Bullet:
    def __init__(self, x, y):
        self.image = pygame.image.load("assets/bullet1.png")
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -10
        self.speed_x = 0
        self.speed_y = self.speed
    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
    def off_screen(self):
        return self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0
    def draw(self, screen):
        screen.blit(self.image, self.rect)

#Class Enemy
class Enemy:
    def __init__(self, enemy_type="random"):
        if enemy_type == "random":
            type_chance = random.random()
            if type_chance < 0.6:
                enemy_type = "small"
            elif type_chance < 0.9:
                enemy_type = "medium"
            else:
                enemy_type = "large" 
        self.type = enemy_type
        if self.type == "small":
            self.image = pygame.image.load("assets/asteroid1.png")
            self.hp = 1
            self.speed = 5
        elif self.type == "medium":
            self.image = pygame.image.load("assets/asteroid2.png")
            self.hp = 3
            self.speed = 3
        else:
            self.image = pygame.image.load("assets/asteroid3.png")
            self.hp = 5
            self.speed = 2
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH - 50), -50))
    def move(self):  
        self.rect.y += self.speed
    def off_screen(self):
        return self.rect.top > HEIGHT
    def draw(self, screen):
        screen.blit(self.image, self.rect)

#Class Boss
class Boss:
    def __init__(self):
        self.bullets = []
        self.shoot_timer = 1
        self.image = pygame.image.load("assets/enemy1.png")
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(WIDTH // 2, -50))
        self.speed = 2
        self.hp = 20 
        self.direction = 1
        self.hit_timer = 0
        self.spiral_angle = 0
        self.spiral_speed = 5
    def move(self):
        if self.hp > 10:
            self.rect.y += self.speed
            if self.rect.y > 100:
                self.rect.y = 100
                self.rect.x += self.speed * self.direction
                if self.rect.left < 50 or self.rect.right > WIDTH - 50:
                    self.direction *= -1
        else:
            self.speed = 3
            self.rect.y += self.speed
            if self.rect.y > 100:
                self.rect.y = 100
                self.rect.x += self.speed * self.direction * math.sin(self.spiral_angle * 0.1)
                if self.rect.left < 50 or self.rect.right > WIDTH - 50:
                    self.direction *= -1
    def shoot (self):
        num_bullets = 6
        angle_step = 360 / num_bullets
        for i in range(num_bullets):
            angle = math.radians(self.spiral_angle + i * angle_step)
            bullet = Bullet(self.rect.centerx, self.rect.bottom)
            bullet.speed_x = math.sin(angle) * 8
            bullet.speed_y = math.cos(angle) * 8
            self.bullets.append(bullet)
        self.spiral_angle += self.spiral_speed
    def off_screen(self):
        return self.rect.top > HEIGHT
    def draw(self, screen):
        if self.hit_timer > 0:
            red_image = self.original_image.copy()
            red_image.fill((255, 0, 0, 100), special_flags = pygame.BLEND_RGB_MULT)
            screen.blit(red_image, self.rect)
        elif self.hp <= 10:
            phase2_image = self.original_image.copy()
            phase2_image.fill((255, 100, 100, 100), special_flags=pygame.BLEND_RGB_MULT)
            screen.blit(phase2_image, self.rect)
        else:
            screen.blit(self.original_image, self.rect)
        for bullet in self.bullets:
            bullet.draw(screen)
    def update(self, dt):
        self.move()
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.shoot() 
            self.shoot_timer = 1 if self.hp > 10 else 0.5
        for bullet in self.bullets:
            bullet.move()
        self.bullets = [b for b in self.bullets if not b.off_screen()]
        if self.hit_timer > 0:
            self.hit_timer -= dt

#Explosion:
class Explosion:
    def __init__(self, x, y):
        self.image = pygame.image.load("assets/Explosion1.png")
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 0.5
    def update (self, dt):
        self.timer -= dt
    def draw(self, screen):
        screen.blit(self.image, self.rect)

#Class Player
class Player:
    def __init__(self):
        self.hp = 3
        self.image = pygame.image.load("assets/playerbiru.png")
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.speed = 5
        self.bullets = []
        self.hit_timer = 0
    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        self.bullets.append(bullet)
    def draw (self, screen):
        if self.hit_timer > 0:
            red_image = self.original_image.copy()
            red_image.fill((255, 0, 0, 100), special_flags=pygame.BLEND_RGB_MULT)
            screen.blit(red_image, self.rect)
        else:
            screen.blit(self.original_image, self.rect)
        for bullet in self.bullets:
            bullet.draw(screen)
    def update(self, dt):
        if self.hit_timer > 0:
            self.hit_timer -= dt

#Start Screen
def show_start():
    while True:
        screen.blit(background, (0, 0))
        text = font.render("Press SPACE to Start", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return
        clock.tick(60)

#Game Over
def show_game_over(score):
    while True:
        screen.blit(background, (0, 0))
        game_over_text = font.render(f"Game Over!", True, WHITE)
        score_text = font.render(f"Score: {score}", True, WHITE)
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                return
        clock.tick(60)

#Main
def main_game():
    player = Player()
    pygame.time.set_timer(SPAWN_ENEMY, 5000)
    enemies = []
    explosions = []
    score = 0
    destroyed_enemies = 0
    boss = None
    game_over = False
    wave_type = 0
    wave_count = 0
    wave_total = 0
    used_x = []

    def spawn_mini_wave():
        nonlocal wave_count, wave_total, used_x
        if wave_count < wave_total:
            x = random.randint(50, WIDTH - 50)
            while any(abs(x - ux) < 30 for ux in used_x):
                x = random.randint(50, WIDTH - 50)
            used_x.append(x)
            y = random.randint(-150, -50)
            enemy = Enemy("small" if wave_type == 1 else "medium" if wave_type == 2 else "large")
            enemy.rect = enemy.image.get_rect(center=(x, y))
            enemies.append(enemy)
            wave_count += 1
            if wave_count < wave_total:
                pygame.time.set_timer(SPAWN_MINI, 1000)
            else:
                used_x.clear()

    while not game_over:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.shoot()
            if event.type == SPAWN_ENEMY:
                wave_type = random.randint(1, 3)
                wave_count = 0
                wave_total = 3 if wave_type == 1 else 2 if wave_type == 2 else 1
                used_x.clear()
                spawn_mini_wave()
            if event.type == SPAWN_MINI:
                spawn_mini_wave()
        
        player.move()
        player.update(dt)

        for bullet in player.bullets:
            bullet.move()
        player.bullets = [b for b in player.bullets if not b.off_screen()]
        
        for enemy in enemies:
            enemy.move()
        enemies = [e for e in enemies if not e.off_screen()]
     
        for bullet in player.bullets[:]:
            for enemy in enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    player.bullets.remove(bullet)
                    enemy.hp -= 1
                    if enemy.hp <= 0:
                        enemies.remove(enemy)
                        explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                        score += 10
                        destroyed_enemies += 1
                    break

        if destroyed_enemies >= 10 and boss is None:
            boss = Boss()
            pygame.time.set_timer(SPAWN_ENEMY, 0)
            pygame.time.set_timer(SPAWN_MINI, 0)

        if boss:
            boss.update(dt)
            for bullet in player.bullets[:]:
                if bullet.rect.colliderect(boss.rect):
                    player.bullets.remove(bullet)
                    boss.hp -= 1
                    boss.hit_timer = 0.2 
                    if boss.hp <= 0:
                        explosions.append(Explosion(boss.rect.centerx, boss.rect.centery))
                        score += 100
                        boss = None
                        pygame.time.set_timer(SPAWN_ENEMY, 0)
                        destroyed_enemies = 0
                        break
            if boss and player.rect.colliderect(boss.rect):
                player.hp -= 1
                player.hit_timer = 0.2
                if player.hp <= 0:
                    game_over = True
            if boss:
                for bullet in boss.bullets[:]:
                    if bullet.rect.colliderect(player.rect):
                        boss.bullets.remove(bullet)
                        player.hp -= 1
                        player.hit_timer = 0.2
                        if player.hp <= 0:
                            game_over = True

        for enemy in enemies[:]:
            if player.rect.colliderect(enemy.rect):
                enemies.remove(enemy)
                player.hp -= 1
                player.hit_timer = 0.2
                if player.hp <= 0:
                    game_over = True

        for explosion in explosions[:]:
            explosion.update(dt)
            if explosion.timer <= 0:
                explosions.remove(explosion)
        screen.blit(background, (0, 0))
        player.draw(screen)
        
        for enemy in enemies:
            enemy.draw(screen)
        if boss:
            boss_hp_text = font.render(f"Boss Hp: {boss.hp}", True, WHITE)
            screen.blit(boss_hp_text, (WIDTH - boss_hp_text.get_width() - 10, 10))
            boss.draw(screen)
            for bullet in boss.bullets:
                bullet.draw(screen)        
        for explosion in explosions:
            explosion.draw(screen)

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        hp_text = font.render(f"HP: {player.hp}", True, WHITE)
        screen.blit(hp_text, (10, 40))
        pygame.display.update()

    show_game_over(score)

def main():
    while True:
        show_start()
        main_game()
if __name__ == "__main__":
    main()
