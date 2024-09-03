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
SEED_PRICE = 20
TAX_AMOUNT = 50
INITIAL_CROP_GROWTH_TIME = 3  # Initial growth time in seconds

# Setup the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Harvest and Tax Game")

# Clock for managing frame rate
clock = pygame.time.Clock()

# Font for text display
font = pygame.font.Font(None, 36)

# Asset loading status
assets_loaded = True

def preload_assets():
    global farmer_image, crop_seed_image, crop_growing_image, crop_ready_image
    global shop_image, government_office_image, farm_background_image
    global school_image, hospital_image

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

# Preload assets directly
preload_assets()

class Farmer:
    def __init__(self):
        self.image = pygame.transform.scale(farmer_image, (40, 40))
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.speed = 5
    
    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        # Keep the farmer within the screen bounds
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

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

    def plant(self, crop):
        if self.seeds > 0:
            self.seeds -= 1
            return True
        return False

    def pay_taxes(self):
        if self.money >= TAX_AMOUNT:
            self.money -= TAX_AMOUNT
            self.tax_due = False
            self.tax_paid_count += 1
            self.tax_streak += 1  # Increment tax streak
            self.update_seed_price_and_growth_time()
            return True
        return False

    def buy_seeds(self, seed_price, quantity=1):
        total_cost = seed_price * quantity
        if self.money >= total_cost:
            self.money -= total_cost
            self.seeds += quantity
            return True
        return False

    def update_seed_price_and_growth_time(self):
        global crop_growth_time
        if self.tax_due:
            # Increase seed price and growth time if taxes are due
            shop.seed_price = min(shop.seed_price + 2, 50)
            crop_growth_time = min(crop_growth_time + 1, 10)
        else:
            # Gradually reduce seed price and crop growth time
            shop.seed_price = max(shop.seed_price - 1, 2)
            crop_growth_time = max(crop_growth_time - 0.5, 2)
        
        # Special case: if player has a high tax streak
        if self.tax_streak >= 3:
            crop_growth_time = max(crop_growth_time - 0.5, 2)
            shop.seed_price = max(shop.seed_price - 1, 2)
            self.tax_streak = 0  # Reset tax streak
            display_popup(screen, "Crop growth time and seed price reduced!")

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
            if current_time - self.plant_time >= INITIAL_CROP_GROWTH_TIME:  # Dynamic growth time
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
        self.seed_price = SEED_PRICE  # Default seed price is now 20

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Farm:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.background = pygame.transform.scale(farm_background_image, (width, height))
        
        # Randomly place crops within the farm area
        self.crops = [Crop(random.randint(x + 10, x + width - 60), 
                           random.randint(y + 10, y + height - 60)) 
                      for _ in range(10)]

    def plant_crop(self, farmer, player):
        for crop in self.crops:
            if crop.rect.collidepoint(farmer.rect.center):
                if not crop.is_planted:
                    if player.plant(crop):
                        crop.plant()
                        print(f"Planted a crop! Seeds left: {player.seeds}")
                elif crop.is_planted and not crop.is_harvested:
                    if crop.harvest():
                        player.harvest()
                        print(f"Harvested a crop! Money: ${player.money}")

    def grow_crops(self):
        for crop in self.crops:
            crop.grow()

    def draw(self, surface):
        surface.blit(self.background, self.rect.topleft)  # Draw farm background
        for crop in self.crops:
            crop.draw(surface)

class School:
    def __init__(self, x, y):
        self.image = pygame.transform.scale(school_image, (100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.built = False
        self.build_progress = 0  # Track the progress of the building

    def build(self):
        if self.build_progress < 100:
            self.build_progress += 0.5  # Increase progress over time
        if self.build_progress >= 100:
            self.built = True

    def draw(self, surface):
        if self.built:
            surface.blit(self.image, self.rect)

class Hospital:
    def __init__(self, x, y):
        self.image = pygame.transform.scale(hospital_image, (100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.built = False
        self.build_progress = 0  # Track the progress of the building

    def build(self):
        if self.build_progress < 100:
            self.build_progress += 0.5  # Increase progress over time
        if self.build_progress >= 100:
            self.built = True

    def draw(self, surface):
        if self.built:
            surface.blit(self.image, self.rect)

def display_popup(surface, message):
    popup_font = pygame.font.Font(None, 48)
    popup_text = popup_font.render(message, True, WHITE)
    text_rect = popup_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                return

        surface.fill(BROWN)
        surface.blit(popup_text, text_rect)
        pygame.display.flip()
        clock.tick(30)

# Create instances
player = Player()
farmer = Farmer()

# Create a farm area
farm = Farm(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

# Create a government office at the bottom right
government_office = GovernmentOffice(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)

# Create a shop at the bottom left
shop = Shop(0, SCREEN_HEIGHT - 100)

# Create a school and hospital
school = School(SCREEN_WIDTH - 220, SCREEN_HEIGHT - 100)
hospital = Hospital(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 100)

# Game loop
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
    # Handle farmer movement
    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_LEFT]:
        dx = -1
    if keys[pygame.K_RIGHT]:
        dx = 1
    if keys[pygame.K_UP]:
        dy = -1
    if keys[pygame.K_DOWN]:
        dy = 1
    
    farmer.move(dx, dy)

    # Check for planting or harvesting
    if pygame.mouse.get_pressed()[0]:  # Left mouse click
        if farm.rect.collidepoint(farmer.rect.center):
            farm.plant_crop(farmer, player)
        
        # Check if the farmer is at the government office to pay taxes
        if government_office.rect.collidepoint(farmer.rect.center):
            if player.harvest_count >= 5:  # Changed to fixed interval
                if player.pay_taxes():
                    player.harvest_count = 0
                    print(f"Taxes paid! Total: {player.tax_paid_count}")
                    if player.tax_paid_count >= 4 and not school.built:
                        school.build()
                    if player.tax_paid_count >= 6 and not hospital.built:
                        hospital.build()
                else:
                    print("Not enough money to pay taxes or not enough harvests completed!")
        
        # Check if the farmer is at the shop to buy seeds
        if shop.rect.collidepoint(farmer.rect.center):
            if player.buy_seeds(shop.seed_price):
                print(f"Bought seeds! Seeds left: {player.seeds}, Money: ${player.money}")
            else:
                print("Not enough money to buy seeds!")

    # Simulate crop growth
    farm.grow_crops()

    # Update game state based on tax payment
    if player.harvest_count >= 5:  # Changed to fixed interval
        player.tax_due = True

    # Draw everything
    screen.fill(WHITE)
    farm.draw(screen)
    farmer.draw(screen)
    government_office.draw(screen)
    shop.draw(screen)
    school.draw(screen)
    hospital.draw(screen)

    # Display player money and seeds
    money_text = font.render(f"Money: ${player.money}", True, BROWN)
    screen.blit(money_text, (10, 10))

    seeds_text = font.render(f"Seeds: {player.seeds}", True, BROWN)
    screen.blit(seeds_text, (10, 50))

    # Display tax info
    tax_text = font.render(f"Taxes Paid: {player.tax_paid_count}", True, BROWN)
    screen.blit(tax_text, (10, 90))

    # Display seed price
    seed_price_text = font.render(f"Seed Price: ${shop.seed_price}", True, BROWN)
    screen.blit(seed_price_text, (10, 130))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
