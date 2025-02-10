from cider.interfaces.controller.config_wrapper import ConfigurationWrapper
from cider.widgets.enable_disable_base import __EnableDisablePanel
from cider.interfaces.workflows.get_set_session_attribute import (
    SetAttributeValueSessionAction,
    GetAttributeValueSessionAction,
)

import cider.interfaces.actions.actions as ca
from textual.visual import SupportsVisual
from textual.widgets import Button


class TriggerPanel(__EnableDisablePanel):
    def __init__(
        self,
        configuration: ConfigurationWrapper | None,
        session_name: str | None,
        attribute_map: dict,
        content: str | SupportsVisual = "",
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False
    ) -> None:
        """
        Attribute Map has form

        Trigger Label : {
            "attribute_name: str,
            "class_name": str,
            "object_names": List[str],
            "enabled_by_default": bool
        """

        super().__init__(
            configuration,
            session_name,
            content,
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

        self._attribute_map = attribute_map

    def generate_button_list(self):
        if self._session_name is None or self._configuration is None:
            return {}

        session = ca.GetDalObjectAction(self._configuration)(
            self._session_name, "Session")

        # This one is nice and simple!
        for trigger_info in self._attribute_map.values():

            class_name = trigger_info["class_name"]
            trigger_name = trigger_info["attribute_name"]
            object_names = trigger_info["object_names"]

            # Quick consistency check
            current_states = GetAttributeValueSessionAction(self._configuration)(session, class_name, trigger_name, object_names)

            enabled_state = trigger_info.get("enabled_state" , True)
            disabled_state = trigger_info.get("disabled_state" , True)
        
            if not all(s==current_states[0] for s in current_states):
                init_state = enabled_state
            elif current_states[0] != enabled_state or current_states[0] != disabled_state:
                init_state = enabled_state
            else:
                init_state = current_states[0]
            
            # Set initial state of trigger
            trigger_info["enabled"] = init_state
        
            # This should be None
            object_names = trigger_info["object_names"]

            session = ca.GetDalObjectAction(self._configuration)(
                self._session_name, "Session"
            )

            SetAttributeValueSessionAction(self._configuration).action(
                session, class_name, trigger_name, trigger_info["enabled"], object_names
            )
            

        return self._attribute_map

    def check_is_disabled(self, button: str, _) -> bool:
        return not self._button_list.get(button, False)["enabled"]

    def on_button_pressed(self, event: Button.Pressed):
        button_name = event.button.id.replace("_button", "")
        button_name = button_name.replace("_", " ")

        objs_affected = self._button_list.get(button_name, None)

        if objs_affected is None:
            return

        class_name = objs_affected["class_name"]
        object_names = objs_affected["object_names"]
        trigger_name = objs_affected["attribute_name"]

        # We want to flip this!
        if objs_affected["enabled"] == objs_affected.get("enabled_state", True):
            objs_affected["enabled"] = objs_affected.get("disabled_state", False)
        else:
            objs_affected["enabled"] = objs_affected.get("enabled_state", True)
        
        session = ca.GetDalObjectAction(self._configuration)(
            self._session_name, "Session"
        )

        SetAttributeValueSessionAction(self._configuration).action(
            session,
            class_name,
            trigger_name,
            objs_affected["enabled"],
            object_names,
        )
        self.refresh(recompose=True)
