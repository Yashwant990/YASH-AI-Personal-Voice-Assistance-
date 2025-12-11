
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
import threading

class AvatarApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.actor = Actor("models/jarvis_body.glb", {
    "idle": "models/idle_anim.glb",
    "talk": "models/talk_anim.glb"
})

        self.actor.reparentTo(self.render)
        self.actor.setScale(0.5)
        self.actor.setPos(0, 10, 0)
        self.actor.loop("idle")

    def play_talk(self):
        self.actor.play("talk")

    def play_idle(self):
        self.actor.loop("idle")

def launch_avatar():
    app = AvatarApp()
    threading.Thread(target=app.run).start()
    return app
