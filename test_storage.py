from cce.core.storage import load_world, save_world
from cce.core.models import World, Event
w = World(name='Test')
e = Event(id='e1', start_tick=0, end_tick=100, characters=['Hero', 'Villain'])
w.events.append(e)
save_world(w, 'test.json')
w2 = load_world('test.json')
print(w2.events[0].characters)
