# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import ChannelAccount, CardAction, ActionTypes, SuggestedActions


class UserActionQueue:
    def __init__(self):
        self.actions = {}

    def add_user(self, member_id):
        if not self.is_valid_user(member_id):
            self.actions[member_id] = []

    def add_action(self, member_id, action):
        if self.is_valid_user(member_id):
            self.actions[member_id].append(action)

    def is_valid_user(self, member_id):
        if member_id not in self.actions:
            return False
        return True

    def get_user_actions(self, member_id):
        if not self.is_valid_user(member_id):
            return -1
        return '\n'.join(self.actions[member_id])


class MyBot(ActivityHandler):
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.

    action_queue = UserActionQueue()

    async def on_message_activity(self, turn_context: TurnContext):
        text = turn_context.activity.text.lower()
        # await turn_context.send_activity(f"You said {text}")
        response_text = self._process_input(text, turn_context.activity.recipient.id)
        await turn_context.send_activity(MessageFactory.text(response_text))
        return await self._send_suggested_actions(turn_context)

    def _process_input(self, text: str, member_id):
        if text == "1":
            self.action_queue.add_action(member_id=member_id, action="1")
            return f"The article has been added to the widget"
        if text == "2":
            self.action_queue.add_action(member_id=member_id, action="2")
            return f"The article has been replaced in the widget"
        if text == "3":
            self.action_queue.add_action(member_id=member_id, action="3")
            return f"The article has been removed from the widget"
        if text == "4":
            self.action_queue.add_action(member_id=member_id, action="4")
            return f"The article has been removed from the page"
        if text == "5":
            self.action_queue.add_action(member_id=member_id, action="5")
            return f"The following actions have been taken:\n{self.action_queue.get_user_actions(member_id)}"

        return "Please select a valid option."

    async def _send_suggested_actions(self, turn_context: TurnContext):
        reply = MessageFactory.text("What do you want to do?")

        reply.suggested_actions = SuggestedActions(
            actions=[
                CardAction(
                    title="1. Add Article to Widget",
                    type=ActionTypes.im_back,
                    value="1",
                ),
                CardAction(
                    title="2. Replace Article in Widget",
                    type=ActionTypes.im_back,
                    value="2",
                ),
                CardAction(
                    title="3. Remove Article from Widget",
                    type=ActionTypes.im_back,
                    value="3",
                ),
                CardAction(
                    title="4. Remove Article from Page",
                    type=ActionTypes.im_back,
                    value="4",
                ),
                CardAction(
                    title="5. List Actions Taken",
                    type=ActionTypes.im_back,
                    value="5",
                ),
            ]
        )

        return await turn_context.send_activity(reply)

    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        for member in turn_context.activity.members_added:
            self.action_queue.add_user(member.id)
        return await self._send_welcome_message(turn_context)

    async def _send_welcome_message(self, turn_context: TurnContext):
        for member in turn_context.activity.members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    MessageFactory.text(
                        f"Welcome to the test bot {member.name}!"
                    )
                )
                await self._send_suggested_actions(turn_context)


