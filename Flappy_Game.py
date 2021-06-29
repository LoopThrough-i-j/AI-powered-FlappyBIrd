from Flappy_Bird import *
import pickle

gene = pickle.load(open("best.pickle", "rb"))


def draw_window(win, bird, pipes, base, score, AIplaying):

    win.blit(bg_img, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    bird.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    if AIplaying:
        playerStatus = STAT_FONT.render("AI", 1, (255, 255, 255))
    else:
        playerStatus = STAT_FONT.render("Player", 1, (255, 255, 255))
    win.blit(score_label, (SCREENWIDTH - score_label.get_width() - 15, 10))
    win.blit(playerStatus, (5, 10))

    pygame.display.update()


def Play():
    AIplaying = False
    global gene
    global WIN
    win = WIN
    vel = 3

    base = Base(450)
    pipes = [Pipe(SCREENWIDTH)]
    score = 0

    clock = pygame.time.Clock()
    bird = Bird(100, 100)
    run = True
    while run:
        clock.tick(30)

        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                break

        pipe_ind = 0

        if (
            len(pipes) > 1 and bird.x > pipes[0].x + pipes[0].PIPE_TOP.get_width()
        ):  # determine whether to use the first or second
            pipe_ind = 1  # pipe on the screen for neural network input

        bird.move()

        if keys[pygame.K_SPACE]:
            AIplaying = True

        if AIplaying:
            output = gene.activate(
                (
                    bird.y,
                    abs(bird.y - pipes[pipe_ind].height),
                    abs(bird.y - pipes[pipe_ind].bottom),
                )
            )
            if (
                output[0] > 0.5
            ):  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()
        else:
            if keys[pygame.K_UP]:
                bird.jump()
        base.move()
        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            pipe.VEL = vel
            # check for collision
            if pipe.collide(bird, win):
                run = False

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            # can add this line to give more reward for passing through a pipe (not required)

            if score % 5 == 0:
                vel += 1
                base.VEL = vel
            if vel > 4:
                vel = 4

            pipes.append(Pipe(SCREENWIDTH))

        for r in rem:
            pipes.remove(r)

        if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
            run = False

        draw_window(WIN, bird, pipes, base, score, AIplaying)
        AIplaying = False


if __name__ == "__main__":
    Play()
