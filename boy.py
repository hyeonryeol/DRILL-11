from pico2d import load_image, get_time, clamp, SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT
from transitions import Machine, State


# ---------------------------------------------------------------
# 상태 클래스: 각 상태가 할 일을 자기 클래스 안에 모아 둔다.
#  enter() : 상태에 들어갈 때 한 번 (Entry action)
#  exit()  : 상태에서 나갈 때 한 번 (Exit action)
#  do()    : 상태에 머무르는 동안 매 프레임 (Do activity)
#  draw()  : 상태에 맞는 그림 그리기
# ---------------------------------------------------------------
class Idle:
    def __init__(self, boy):
        self.boy = boy

    def enter(self):
        self.boy.idle_start_time = get_time()  # IDLE에 들어올 때마다 5초 타이머 시작

    def exit(self):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8
        if get_time() - self.boy.idle_start_time >= 5:
            self.boy.time_out()

    def draw(self):
        boy = self.boy
        if boy.face_dir == 1:
            boy.image.clip_draw(boy.frame * 100, 300, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(boy.frame * 100, 200, 100, 100, boy.x, boy.y)


class Sleep:
    def __init__(self, boy):
        self.boy = boy

    def enter(self):
        pass

    def exit(self):
        pass

    def do(self):
        pass  # 자는 동안은 프레임을 멈춰서 들썩이지 않게

    def draw(self):
        boy = self.boy
        # IDLE 그림을 90도 눕혀서 누워 자는 모습으로 그림
        if boy.face_dir == 1:
            boy.image.clip_composite_draw(boy.frame * 100, 300, 100, 100,
                                          3.141592 / 2, '', boy.x - 25, boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(boy.frame * 100, 200, 100, 100,
                                          -3.141592 / 2, '', boy.x + 25, boy.y - 25, 100, 100)


class Run:
    def __init__(self, boy):
        self.boy = boy

    def enter(self):
        pass

    def exit(self):
        pass

    def do(self):
        boy = self.boy
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 10
        boy.x = clamp(50, boy.x, 800 - 50)  # 소년 폭 100의 절반만큼 안쪽에서 멈춰 화면 밖으로 안 나감

    def draw(self):
        boy = self.boy
        if boy.face_dir == 1:
            boy.image.clip_draw(boy.frame * 100, 100, 100, 100, boy.x, boy.y)  # 오른쪽 달리기 줄
        else:
            boy.image.clip_draw(boy.frame * 100, 0, 100, 100, boy.x, boy.y)    # 왼쪽 달리기 줄


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0                    # 달리는 방향: 1 오른쪽, -1 왼쪽, 0 멈춤
        self.right_pressed = False      # 방향키를 누르고 있는지 기억
        self.left_pressed = False
        self.image = load_image('animation_sheet.png')

        # 상태 이름 -> 상태 객체
        self.state_objects = {
            'IDLE': Idle(self),
            'SLEEP': Sleep(self),
            'RUN': Run(self),
        }
        self.machine = Machine(
            model=self,
            states=[State(name, on_enter=obj.enter, on_exit=obj.exit)
                    for name, obj in self.state_objects.items()],
            transitions=[
                {'trigger': 'time_out', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'space_down', 'source': 'SLEEP', 'dest': 'IDLE'},
                {'trigger': 'dir_down', 'source': 'IDLE', 'dest': 'RUN'},
                {'trigger': 'dir_up', 'source': 'RUN', 'dest': 'IDLE'},
            ],
            initial='IDLE',
            auto_transitions=False,
            ignore_invalid_triggers=True,  # 지금 상태에 없는 이벤트는 에러 없이 무시
        )
        self.state_objects[self.state].enter()  # 처음 상태는 on_enter가 불리지 않으므로 직접 호출

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            self.space_down()
            return

        if event.type not in (SDL_KEYDOWN, SDL_KEYUP) or event.key not in (SDLK_LEFT, SDLK_RIGHT):
            return
        pressed = event.type == SDL_KEYDOWN
        if event.key == SDLK_RIGHT:
            self.right_pressed = pressed
        else:
            self.left_pressed = pressed

        # 왼쪽/오른쪽을 따로 상태로 나누지 않고, 방향(dir)만 바꿔서 하나의 RUN으로 처리
        key_dir = self.right_pressed - self.left_pressed
        if key_dir != 0:
            self.dir_down()
            if self.state == 'RUN':
                self.dir = self.face_dir = key_dir
        else:
            self.dir_up()   # 방향키를 모두 떼면(또는 양쪽을 다 누르면) IDLE로

    def update(self):
        self.state_objects[self.state].do()

    def draw(self):
        self.state_objects[self.state].draw()
