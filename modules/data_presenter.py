import logging
from modules.data_render import DataRender


class DataPresenter():
    def __init__(self, chat_config, db_config):
        # all aggregated data for displaying
        self.__data = DataRender(
            chat_config=chat_config,
            db_config=db_config
        ).get_rendered_data()

        # current around using for displaying its data
        self.__current_around = ''
        self.__current_around_data = {}

        # current type of stat from main menu
        self.__main_stat_type = ''

        # selected flat type for displaying data
        self.__flat_type = ''

        # selected rb name for displaying data
        self.__rb_name = ''

    def get_consolidation_arounds_report(self) -> str:
        return self.__data['cons_report_text_cut']

    def get_arounds_names(self) -> list:
        return [row['arround_title'] for row in self.__data['arround_list']]

    def get_cut_cons_report(self) -> str:
        return self.__current_around_data[self.__main_stat_type]['cons_report_text_cut']

    def get_full_cons_report(self) -> str:
        return self.__current_around_data[self.__main_stat_type]['cons_report_text_full']

    def get_count_flats_all_text(self) -> str:
        return self.__current_around_data[self.__main_stat_type]['count_flats_all_text']

    def get_each_rb_all_text(self) -> str:
        return self.__current_around_data[self.__main_stat_type]['each_rb_all_text']

    def get_flat_types(self) -> list:
        return [row['type'] for row in self.__current_around_data[self.__main_stat_type]['count_flats_all_list']]

    def get_rb_names(self) -> list:
        return [row['type'] for row in self.__current_around_data[self.__main_stat_type]['each_rb_all_list']]

    def get_all_using_flat_types(self) -> list:
        all_types = []
        for around in self.__data['arround_list']:
            all_types += [row['type'] for row in around['new_stat']['count_flats_all_list']] + \
                         [row['type'] for row in around['old_stat']['count_flats_all_list']] + \
                         [row['type'] for row in around['sell_stat']['count_flats_all_list']]
        return list(set(all_types))

    def get_all_using_rb_names(self) -> list:
        all_types = []
        for around in self.__data['arround_list']:
            all_types += [row['type'] for row in around['new_stat']['each_rb_all_list']] + \
                         [row['type'] for row in around['old_stat']['each_rb_all_list']] + \
                         [row['type'] for row in around['sell_stat']['each_rb_all_list']]
        return list(set(all_types))

    def get_selected_flat_type_data(self) -> str:
        for row in self.__current_around_data[self.__main_stat_type]['count_flats_all_list']:
            if row['type'] == self.__flat_type:
                return row['text']

    def get_selected_rb_name_data(self) -> str:
        for row in self.__current_around_data[self.__main_stat_type]['each_rb_all_list']:
            if row['type'] == self.__rb_name:
                return row['text']

    def get_rb_names_by_selected_flat_type(self):
        for row in self.__current_around_data[self.__main_stat_type]['each_flats_rb_list']:
            if row['rooms_count_title'] == self.__flat_type:
                return [sub_row['type'] for sub_row in row['all_types_list']]

    def get_flat_types_by_selected_rb_name(self):
        for row in self.__current_around_data[self.__main_stat_type]['each_rb_flats_list']:
            if row['rb_title'] == self.__rb_name:
                return [sub_row['type'] for sub_row in row['all_types_list']]

    def get_rb_data_by_flat_type(self, flat_type: str) -> str:
        for row in self.__current_around_data[self.__main_stat_type]['each_flats_rb_list']:
            if row['rooms_count_title'] == self.__flat_type:
                for sub_row in row['all_types_list']:
                    if sub_row['type'] == flat_type:
                        return sub_row['text']

    def get_flat_type_data_by_rb_name(self, rb_name: str) -> str:
        for row in self.__current_around_data[self.__main_stat_type]['each_rb_flats_list']:
            if row['rb_title'] == self.__rb_name:
                for sub_row in row['all_types_list']:
                    if sub_row['type'] == rb_name:
                        return sub_row['text']

    def get_each_rb_data_by_flat_type(self) -> str:
        for row in self.__current_around_data[self.__main_stat_type]['each_flats_rb_list']:
            if row['rooms_count_title'] == self.__flat_type:
                return row['all_types_text']

    def get_each_flat_type_by_rb_name(self) -> str:
        for row in self.__current_around_data[self.__main_stat_type]['each_rb_flats_list']:
            if row['rb_title'] == self.__rb_name:
                return row['all_types_text']

    def set_current_around(self, arround_title: str) -> None:
        self.__current_around = arround_title
        for row in self.__data['arround_list']:
            if row['arround_title'] == arround_title:
                self.__current_around_data = row

    def set_main_stat_type(self, main_menu_item: str) -> None:
        self.__main_stat_type = main_menu_item

    def set_flat_type(self, flat_type) -> None:
        self.__flat_type = flat_type

    def set_rb_name(self, rb_name) -> None:
        self.__rb_name = rb_name
