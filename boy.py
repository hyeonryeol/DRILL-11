from pico2d import load_image, get_time
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


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.image = load_image('animation_sheet.png')

        # 상태 이름 -> 상태 객체
        self.state_objects = {
            'IDLE': Idle(self),
            'SLEEP': Sleep(self),
        }
        self.machine = Machine(
            model=self,
            states=[State(name, on_enter=obj.enter, on_exit=obj.exit)
                    for name, obj in self.state_objects.items()],
            transitions=[
                {'trigger': 'time_out', 'source': 'IDLE', 'dest': 'SLEEP'},
            ],
            initial='IDLE',
            auto_transitions=False,
            ignore_invalid_triggers=True,  # 지금 상태에 없는 이벤트는 에러 없이 무시
        )
        self.state_objects[self.state].enter()  # 처음 상태는 on_enter가 불리지 않으므로 직접 호출

    def update(self):
        self.state_objects[self.state].do()

    def draw(self):
        self.state_objects[self.state].draw()
