# Use Cases

Below are some use cases, some of which could make it into the video, some of which we should build the product around.

(Note: I imagine startups being built to turn the 01 into these, but the first one is simple enough, I think we should just build it in as the default for the light body.)

<br>

## Executive assistant / Bookmark for your life / Productivity tool

Lets you offload a bunch of executive functions related to time and memory management— it intelligently orders your lists, batches tasks, and reminds you of scheduled items. "I just promised Ben I would do X." "Okay, I'll remind you of that later."

I imagine telling it everything I need to do, adding items to that list throughout the day, then having it guide me through the list one item at a time. **I imagine it answering the question "what should I be doing right now?"**

(One of my motivations: _I never want to see my full list._ It's overwhelming. I want this to break it down into tiny steps, then I just do them.)

Once you've started a task, it checks in with you when that item should be completed (based on its estimate, which could be informed by previous information re: how long it took to finish some task).

### Example

**User:** Hey, here's what I need to do today...

**Assistant:** Sounds good! I'll add those items to your list *in an order that I think would be most effective*, then let's start on that first item.

```python
tasks += ... # Add items to the list
tasks[0] # Print the first item on the list
```
```
# Output: Make coffee.
```

**Assistant:** First, let's make coffee. I think that will take you ~5 minutes, so I'll check in with you then.

```python
# I'll use the computer.clock to schedule a reminder for 5 minutes from now.
reminder_time = datetime.now() + timedelta(minutes=5)
computer.clock.schedule(reminder_time, "Ask the user if they've finished making coffee.")
```

<br>

_... 5 minutes passes ..._

<br>

**Computer:** "Ask the user if they've finished making coffee."

**Assistant:** It's been 5 minutes. Have you finished making coffee?

**User:** Yes.

**Assistant:** Great! I hope it's delicious. I'll check that off and we can start on the next item.

```python
tasks = tasks[1:] # Remove the first item from the list
tasks[0] # Print the new first item on the list
```

...

<br>

## Doctor

I imagine taking a photo of something, like dry skin, and asking questions about what I can do.

It could do RAG over [Medline Plus](https://medlineplus.gov/) to give me grounded information. It could use [Moondream](https://github.com/vikhyat/moondream) locally.

<br>

## Wikipedia in the middle of nowhere

RAG over Wikipedia, updates every day (if it's connected to the internet, otherwise updates next time it's connected to the internet).

I imagine building a windmill with it— walking through the steps, it might have access to some schematics? And could help me calculate anything I need to calculate / work with the materials I have access to.

<br>

## Toys

The ultimate build-a-bear— you press its paw and you can learn anything from this. Always speaks very simply.

<br>

## Chief of staff

Interacts with my computer(s) or interpreter(s) to retrieve information / get something done.
