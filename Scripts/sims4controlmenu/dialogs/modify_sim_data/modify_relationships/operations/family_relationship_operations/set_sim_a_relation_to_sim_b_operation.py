"""
The Sims 4 Control Menu is licensed under the Creative Commons Attribution 4.0 International public license (CC BY 4.0).
https://creativecommons.org/licenses/by/4.0/
https://creativecommons.org/licenses/by/4.0/legalcode

Copyright (c) COLONOLNUTTY
"""
from typing import Callable, Any

from protocolbuffers.Localization_pb2 import LocalizedString
from relationships.relationship_bit import RelationshipBit
from sims.sim_info import SimInfo
from sims4.resources import Types
from sims4communitylib.enums.relationship_bits_enum import CommonRelationshipBitId
from sims4communitylib.services.common_service import CommonService
from sims4communitylib.utils.common_function_utils import CommonFunctionUtils
from sims4communitylib.utils.common_resource_utils import CommonResourceUtils
from sims4communitylib.utils.localization.common_localization_utils import CommonLocalizationUtils
from sims4communitylib.utils.sims.common_relationship_utils import CommonRelationshipUtils
from sims4controlmenu.commonlib.dialogs.option_dialogs.common_choose_button_option_dialog import \
    CommonChooseButtonOptionDialog
from sims4controlmenu.commonlib.dialogs.option_dialogs.options.common_dialog_button_option import \
    CommonDialogButtonOption
from sims4controlmenu.commonlib.dialogs.option_dialogs.options.common_dialog_response_option_context import \
    CommonDialogResponseOptionContext
from sims4controlmenu.dialogs.modify_sim_data.double_sim_operation import S4CMDoubleSimOperation
from sims4controlmenu.dialogs.modify_sim_data.enums.string_identifiers import S4CMSimControlMenuStringId
from sims4controlmenu.enums.string_identifiers import S4CMStringId
from sims4controlmenu.logging.has_s4cm_log import HasS4CMLog
from sims4controlmenu.modinfo import ModInfo


class S4CMSetSimAAsRelationToSimBOperation(S4CMDoubleSimOperation, HasS4CMLog, CommonService):
    """Set Sim A to have a family relation with Sim B"""

    # noinspection PyMissingOrEmptyDocstring
    @property
    def log_identifier(self) -> str:
        return 's4cm_set_sim_as_relation_to_sim'

    @property
    def relationship_bit_id(self) -> CommonRelationshipBitId:
        """The relationship bit to add to Sim A for Sim B."""
        raise NotImplementedError()

    @property
    def opposite_relationship_bit_id(self) -> CommonRelationshipBitId:
        """The relationship bit to add to Sim B for Sim A."""
        raise NotImplementedError()

    @property
    def _display_name(self) -> int:
        if self.__display_name is None:
            relationship_bit_id: int = self.relationship_bit_id
            relationship_bit: RelationshipBit = CommonResourceUtils.load_instance(Types.RELATIONSHIP_BIT, relationship_bit_id)
            if relationship_bit is None:
                self.__display_name = 0
            # noinspection PyUnresolvedReferences
            self.__display_name = relationship_bit.display_name
        return self.__display_name

    @property
    def _should_update_family_tree(self) -> bool:
        return True

    def __init__(self) -> None:
        super().__init__()
        self.__display_name = None

    def has_relation(self, sim_info_a: SimInfo, sim_info_b: SimInfo) -> bool:
        """has_relation(sim_info_a, sim_info_b)

        Determine whether or not two Sims have the relationship of this operation.

        :param sim_info_a: An instance of a Sim.
        :type sim_info_a: SimInfo
        :param sim_info_b: An instance of a Sim.
        :type sim_info_b: SimInfo
        :return: True, if Sim A has the relation to Sim B. False, if not.
        :rtype: bool
        """
        return CommonRelationshipUtils.has_relationship_bit_with_sim(sim_info_b, sim_info_a, self.relationship_bit_id)

    # noinspection PyMissingOrEmptyDocstring
    def run(self, sim_info_a: SimInfo, sim_info_b: SimInfo, on_completed: Callable[[bool], None]=CommonFunctionUtils.noop) -> bool:
        if not self._should_update_family_tree:
            self._add_relationship_bits(sim_info_a, sim_info_b)
            on_completed(True)
            return True

        def _on_yes_selected(_: str, __: Any):
            def _on_family_tree_updated(result: bool):
                if result:
                    self._add_relationship_bits(sim_info_a, sim_info_b)
                on_completed(result)

            self._update_family_tree(sim_info_a, sim_info_b, on_completed=_on_family_tree_updated)

        def _on_no_selected(_: str, __: Any):
            self._add_relationship_bits(sim_info_a, sim_info_b)
            on_completed(True)

        option_dialog = CommonChooseButtonOptionDialog(
            ModInfo.get_identity(),
            S4CMSimControlMenuStringId.UPDATE_FAMILY_TREE_TITLE,
            S4CMSimControlMenuStringId.UPDATE_FAMILY_TREE_DESCRIPTION,
            previous_button_text=S4CMStringId.CANCEL,
            include_previous_button=True,
            on_previous=lambda: on_completed(False),
            on_close=lambda: on_completed(False)
        )

        option_dialog.add_option(
            CommonDialogButtonOption(
                'Yes',
                'YES',
                CommonDialogResponseOptionContext(
                    S4CMStringId.YES
                ),
                on_chosen=_on_yes_selected
            )
        )

        option_dialog.add_option(
            CommonDialogButtonOption(
                'No',
                'NO',
                CommonDialogResponseOptionContext(
                    S4CMStringId.NO
                ),
                on_chosen=_on_no_selected
            )
        )

        option_dialog.show()
        return True

    def _add_relationship_bits(self, sim_info_a: SimInfo, sim_info_b: SimInfo) -> bool:
        self.log.format_with_message('Setting Sim A as relation to Sim B', sim_a=sim_info_a, sim_b=sim_info_b, relation_id=self.relationship_bit_id)
        result = CommonRelationshipUtils.add_relationship_bit(sim_info_b, sim_info_a, self.relationship_bit_id)
        if result:
            opposite_relationship_bit_id = self.opposite_relationship_bit_id
            if opposite_relationship_bit_id != -1:
                self.log.format_with_message('Setting Sim B to have opposite relation with Sim A', sim_a=sim_info_a, sim_b=sim_info_b, relation_id=self.relationship_bit_id)
                result = CommonRelationshipUtils.add_relationship_bit(sim_info_a, sim_info_b, opposite_relationship_bit_id)
        return result

    def _update_family_tree(self, sim_info_a: SimInfo, sim_info_b: SimInfo, on_completed: Callable[[bool], None]=CommonFunctionUtils.noop) -> bool:
        on_completed(True)
        return True

    def get_display_name(self, sim_info_a: SimInfo, sim_info_b: SimInfo) -> LocalizedString:
        """get_display_name(sim_info_a, sim_info_b)

        Create a display name for the relationship bit option.

        :param sim_info_a: An instance of a Sim.
        :type sim_info_a: SimInfo
        :param sim_info_b: An instance of a Sim.
        :type sim_info_b: SimInfo
        :return: A localized string.
        :rtype: LocalizedString
        """
        return CommonLocalizationUtils.create_localized_string(self._display_name, tokens=(sim_info_a, sim_info_b))