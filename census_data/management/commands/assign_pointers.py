from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from census_data.models import CensusTable, CensusTablePointer


class Command(BaseCommand):
    help = "Load generated indicators"

    def add_arguments(self, parser):
        # todo: add arguments that map to the `load_census_boundaries.run()` ones
        pass

    def handle(self, *args, **options):
        estimates = CensusTable.objects.filter(table_id__endswith='E')

        for estimate in estimates:
            table_id = estimate.table_id[0:-1]
            print(table_id, end=': ')
            # find pointer for estimate
            pointer, was_created = CensusTablePointer.objects.get_or_create(
                table_id=table_id,
                value_table=estimate,
                dataset='ACS5',
            )
            print('🆕' if was_created else '✔️️', end=' - ')
            if pointer.moe_table:
                print('⏭ SKIPPED')
                continue

            # get moe for estimate
            try:
                moe = CensusTable.objects.get(table_id__startswith=table_id, table_id__endswith='M')
            except ObjectDoesNotExist:
                if was_created:
                    pointer.save()
                    print('💾 SAVED WITHOUT MOE')
                else:
                    print('❌ NO MOE')
                continue

            # add moe
            pointer.moe_table = moe
            pointer.save()
            print('💾 SAVED')
