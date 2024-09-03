import pygame
import random
import time
import sys

# Initialize Pygame
pygame.init()

# Constants
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 30

# Setup the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Harvest and Tax Game")

# Clock for managing frame rate
clock = pygame.time.Clock()

# Font for text display
font = pygame.font.Font(None, 36)

# Load images
farmer_image = pygame.image.load('assets/farmer.png').convert_alpha()
crop_seed_image = pygame.image.load('assets/crop_seed.png').convert_alpha()
crop_growing_image = pygame.image.load('assets/crop_growing.png').convert_alpha()
crop_ready_image = pygame.image.load('assets/crop_ready.png').convert_alpha()
shop_image = pygame.image.load('assets/shop.png').convert_alpha()
government_office_image = pygame.image.load('assets/government_office.png').convert_alpha()
farm_background_image = pygame.image.load('assets/farm_background.png').convert_alpha()
school_image = pygame.image.load('assets/school.png').convert_alpha()
hospital_image = pygame.image.load('assets/hospital.png').convert_alpha()

# Scale the farm background to fill the screen
farm_background_image = pygame.transform.scale(farm_background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))


class Farmer:
    def __init__(self):
        self.image = pygame.transform.scale(farmer_image, (40, 40))
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.speed = 5
    
    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Player:
    def __init__(self):
        self.money = 50
        self.harvest_count = 0
        self.seeds = 5
        self.tax_due = False
        self.tax_paid_count = 0
        self.tax_streak = 0  # Track consecutive tax payments
    
    def harvest(self):
        self.money += 30
        self.harvest_count += 1

    def plant(self):
        if self.seeds > 0:
            self.seeds -= 1
            return True
        return False

    def pay_taxes(self, tax_amount):
        if self.money >= tax_amount:
            self.money -= tax_amount
            self.tax_due = False
            self.tax_paid_count += 1
            self.tax_streak += 1  # Increment tax streak
            return True
        return False

    def buy_seeds(self, seed_price, quantity=1):
        total_cost = seed_price * quantity
        if self.money >= total_cost:
            self.money -= total_cost
            self.seeds += quantity
            return True
        return False


class Crop:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.is_planted = False
        self.is_harvested = False
        self.growth_stage = 0  # 0: not planted, 1: planted, 2: ready to harvest
        self.plant_time = 0  # Track when the crop was planted

    def plant(self):
        self.is_planted = True
        self.growth_stage = 1
        self.plant_time = time.time()  # Record the time when the crop is planted

    def grow(self):
        if self.is_planted and not self.is_harvested:
            current_time = time.time()
            if current_time - self.plant_time >= 3:  # Dynamic growth time (e.g., 3 seconds)
                self.growth_stage = 2  # Crop is now ready to harvest

    def harvest(self):
        if self.is_planted and self.growth_stage == 2 and not self.is_harvested:
            self.is_harvested = True
            return True
        return False

    def draw(self, surface):
        if self.is_planted and not self.is_harvested:
            if self.growth_stage == 1:
                surface.blit(crop_growing_image, self.rect)
            elif self.growth_stage == 2:
                surface.blit(crop_ready_image, self.rect)
        else:
            surface.blit(crop_seed_image, self.rect)


class GovernmentOffice:
    def __init__(self, x, y):
        self.image = pygame.transform.scale(government_office_image, (100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Shop:
    def __init__(self, x, y):
        self.image = pygame.transform.scale(shop_image, (100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.seed_price = 20  # Default seed price is now 20

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Farm:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.background = pygame.transform.scale(farm_background_image, (width, height))
        self.crops = []

        # Generate initial crops
        self.generate_new_crop()

    def generate_new_crop(self):
        new_crop = Crop(random.randint(self.rect.x + 10, self.rect.x + self.rect.width - 60),
                        random.randint(self.rect.y + 10, self.rect.y + self.rect.height - 60))
        self.crops.append(new_crop)

    def plant_crop(self, farmer, player):
        for crop in self.crops:
            if crop.rect.collidepoint(farmer.rect.center):
                if not crop.is_planted:
                    if player.plant():
                        crop.plant()
                        print(f"Planted a crop! Seeds left: {player.seeds}")
                elif crop.is_planted and not crop.is_harvested:
                    if crop.harvest():
                        player.harvest()
                        print(f"Harvested a crop! Money: ${player.money}")
                        self.crops.remove(crop)  # Remove harvested crop
                        self.generate_new_crop()  # Add a new crop location

    def grow_crops(self):
        for crop in self.crops:
            crop.grow()

    def draw(self, surface):
        surface.blit(self.background, self.rect.topleft)  # Draw farm background
        for crop in self.crops:
            crop.draw(surface)


def main():
    farmer = Farmer()
    player = Player()
    farm = Farm(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    government_office = GovernmentOffice(820, 10)
    shop = Shop(10, 10)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        farmer.move(dx, dy)

        if keys[pygame.K_SPACE]:
            farm.plant_crop(farmer, player)
            if shop.rect.collidepoint(farmer.rect.center):
                if player.buy_seeds(shop.seed_price):
                    print(f"Bought seeds! Seeds left: {player.seeds}, Money: ${player.money}")
                else:
                    print("Not enough money to buy seeds!")
            if government_office.rect.collidepoint(farmer.rect.center):
                tax_amount = 10  # Define the tax amount
                if player.pay_taxes(tax_amount):
                    print(f"Paid taxes! Money: ${player.money}, Taxes Paid: {player.tax_paid_count}")
                else:
                    print("Not enough money to pay taxes!")

        farm.grow_crops()

        # Draw everything
        screen.fill(BROWN)
        farm.draw(screen)
        farmer.draw(screen)
        government_office.draw(screen)
        shop.draw(screen)

        # Display player's stats
        money_text = font.render(f"Money: ${player.money}", True, WHITE)
        seeds_text = font.render(f"Seeds: {player.seeds}", True, WHITE)
        screen.blit(money_text, (10, 10))
        screen.blit(seeds_text, (10, 40))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
