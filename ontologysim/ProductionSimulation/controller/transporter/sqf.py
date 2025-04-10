import operator
from collections import defaultdict

from ontologysim.ProductionSimulation.sim.Enum import Label, Queue_Enum

from .base import TransporterController


class TransporterController_SQF(TransporterController):
    """
    calculates the next product based on the shortest queue

    """

    def sort_products_on_transporter(self, transport_onto):
        """
        sort all products on transporter

        :param transport_onto:
        :return: [[product_name,time (int)]]
        """
        event_list = []

        queue_list = transport_onto.has_for_transp_queue

        for queue in queue_list:
            for position in queue.has_for_position:
                for product in position.has_for_product:
                    if (
                        product.blocked_for_transporter == 0
                        and self.transport.end_queue_allowed(transport_onto, product)
                    ):
                        # event_onto_list=self.transport.simCore.onto.search(has_for_position_event=position,is_event_logger_of=self.transport.simCore.onto[Label.Logger.value+"0"])
                        event_onto_list = [
                            event
                            for event in position.is_position_event_of
                            if self.transport.simCore.onto[
                                Label.ShortTermLogger.value + "0"
                            ]
                            in event.is_event_short_term_logger_of
                        ]

                        # for event in event_onto_list:
                        for event in event_onto_list:
                            if event.type == Queue_Enum.Change.value:
                                event_list.append(
                                    [product.name, event.time, queue.current_size]
                                )

        event_list.sort(key=lambda x: x[1])

        res = defaultdict(list)

        for k, v, w in event_list:
            res[k].append([v, w])

        products_on_transporter = [[k, v[-1][0], v[-1][1]] for k, v in res.items()]

        products_on_transporter = sorted(
            products_on_transporter, key=operator.itemgetter(1)
        )
        products_on_transporter = sorted(
            products_on_transporter, key=operator.itemgetter(2)
        )

        return products_on_transporter

    def sort_products_not_on_transporter(self, transport_onto=None):
        """
        sort all products not on transporter

        :param transport_onto:
        :return: [[product_name,time (int)]]
        """
        event_list = []
        queue_list = self.transport.get_queue_transportation_allowed(transport_onto)
        for queue in queue_list:
            for position in queue.has_for_position:
                for product in position.has_for_product:
                    if (
                        product.blocked_for_transporter == 0
                        and self.transport.end_queue_allowed(transport_onto, product)
                    ):
                        event_onto_list = [
                            event
                            for event in position.is_position_event_of
                            if self.transport.simCore.onto[
                                Label.ShortTermLogger.value + "0"
                            ]
                            in event.is_event_short_term_logger_of
                        ]

                        for event in event_onto_list:
                            if event.type == Queue_Enum.Change.value:
                                event_list.append(
                                    [product.name, event.time, queue.current_size]
                                )

        event_list.sort(key=lambda x: x[1])

        res = defaultdict(list)

        for k, v, w in event_list:
            res[k].append([v, w])

        products_not_on_transporter = [[k, v[-1][0], v[-1][1]] for k, v in res.items()]

        products_not_on_transporter = sorted(
            products_not_on_transporter, key=operator.itemgetter(1)
        )
        products_not_on_transporter = sorted(
            products_not_on_transporter, key=operator.itemgetter(2)
        )

        return products_not_on_transporter

    def sort_products(self, products_on_transporter, products_not_on_transporter):
        """
        combines the sort on transporter and not on transporter with the sort product method

        :param products_on_transporter:
        :param products_not_on_transporter:
        """
        type_on = "on"
        type_not_on = "not_on"
        elements = products_on_transporter + products_not_on_transporter
        type_list = [type_on] * len(products_on_transporter) + [type_not_on] * len(
            products_not_on_transporter
        )

        for x, y in zip(elements, type_list):
            x.append(y)

        elements = sorted(elements, key=operator.itemgetter(1))
        elements = sorted(elements, key=operator.itemgetter(2))

        return elements
