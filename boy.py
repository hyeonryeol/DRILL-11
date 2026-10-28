from pico2d import load_image
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
        pass

    def exit(self):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + 1) % 8

    def draw(self):
        boy = self.boy
        if boy.face_dir == 1:
            boy.image.clip_draw(boy.frame * 100, 300, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(boy.frame * 100, 200, 100, 100, boy.x, boy.y)


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.image = load_image('animation_sheet.png')

        # 상태 이름 -> 상태 객체
        self.state_objects = {
            'IDLE': Idle(self),
        }
        self.machine = Machine(
            model=self,
            states=[State(name, on_enter=obj.enter, on_exit=obj.exit)
                    for name, obj in self.state_objects.items()],
            transitions=[],
            initial='IDLE',
            auto_transitions=False,
            ignore_invalid_triggers=True,  # 지금 상태에 없는 이벤트는 에러 없이 무시
        )
        self.state_objects[self.state].enter()  # 처음 상태는 on_enter가 불리지 않으므로 직접 호출

    def update(self):
        self.state_objects[self.state].do()

    def draw(self):
        self.state_objects[self.state].draw()
