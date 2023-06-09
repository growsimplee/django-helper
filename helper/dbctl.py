import logging
import re
from django.contrib.postgres.search import SearchVector
from django.db.models import Sum,Count,Value,F
from django.db.models import CharField
from django.db.models.functions import Concat
from django.db import transaction
from django.db.models import Q

logger = logging.getLogger('django')


class BaseDbctl:
    model = None
    search_fields = []
    aggregate_column = None
    id_key_columns= []
    int_key_columns = []
    
    def get_by_id(self, pk):
        return self.model.objects.filter(pk=pk).first()

    def filter_data(self, **args):
        return self.model.objects.filter(**args)

    def fetch(self, filters={}, exclude= {}, term=None): 
        queryset = self.model.objects.filter(**filters).exclude(**exclude)
        if term:
            search_query = Q()
            words = term.split(",")
            for word in words:
                search_query = search_query | Q(search__icontains = word)
            return queryset.annotate(search = SearchVector(*self.search_fields)).filter(search_query)
            # if(bool(re.match('^[a-zA-Z0-9]*$',term))==True):
            #     search_filters = {"search__icontains":term}
            # else:
            #     search_filters = {"search":re.escape(term)}
            # return queryset.annotate(search=SearchVector(*self.search_fields)).filter(**search_filters)
        else :
            return queryset
    
    def aggregate(self, filters = {}, exclude = {}, values=[]):
        queryset = self.model.objects.filter(**filters).exclude(**exclude)
        annotate_dict = {
            f"{self.aggregate_column}_sum" : Sum(self.aggregate_column),
            f"{self.aggregate_column}_count": Count(self.aggregate_column)
        }
        return queryset.values(*values).annotate(**annotate_dict).order_by()

    def save(self, **kwargs):
        obj = self.model.objects.create(**kwargs)
        obj.save()
        logger.info(f'object saved {obj}')
        return obj

    def bulk_create(self, obj_data_array):
        obj_arr = [self.model(**x) for x in obj_data_array]
        created = self.model.objects.bulk_create(obj_arr, ignore_conflicts= True)
        return created

    def common_update(self, filters = {}, exclude = {}, update_data ={}):
        return self.model.objects.filter(**filters).exclude(**exclude).update(**update_data)

    def bulk_update_or_create(self, obj_data_array):
        mapping = {}
        concat_policy  = []
        for x in range(len(self.id_key_columns)): 
            concat_policy.append(self.id_key_columns[x])
            if x != len(self.id_key_columns)-1:
                concat_policy.append(Value("-")) 
        first_id_key = self.id_key_columns[0]
        for data in obj_data_array:
            if len(self.id_key_columns) > 1: 
                key = "-".join([(str(int(float(data[x]))) if data[x] else "")if x in self.int_key_columns else data[x] for x in self.id_key_columns ]) 
            else :
                key = int(float(data[first_id_key])) if self.int_key_columns else data[first_id_key]
            mapping[key] = data
        with transaction.atomic():
            if len(concat_policy)== 1:
                existing = {obj.__dict__[first_id_key] : obj for obj in  self.model.objects.filter(**{f"{first_id_key}__in" : mapping.keys()})}
            else:
                existing = {obj.unique_id:obj for obj in self.model.objects.annotate(unique_id = Concat(*concat_policy, output_field=CharField(max_length= 1024))).filter(unique_id__in = list(mapping.keys()))}

            create_objs = [
                self.model(**v) for k, v in mapping.items() if k not in existing
            ]
            created = self.model.objects.bulk_create(create_objs, ignore_conflicts= True)
            update_fields ={}
            update_objs = []
            for key,obj in existing.items():
                update_dict = mapping[key]
                for k, v in update_dict.items() :
                    setattr(obj, k, v)
                update_fields.update(mapping[key])
                update_objs.append(obj)
            if update_objs != []:
                updated = self.model.objects.bulk_update(update_objs,update_fields.keys())
            logger.info(f"{str(self.model)} Created : {len(created)}, Updated: {len(update_objs)}")
            return {"created": len(created), "updated": len(update_objs)}
    
    def bulk_create_missing(self, obj_data_array):
        mapping = {}
        concat_policy  = []
        for x in range(len(self.id_key_columns)): 
            concat_policy.append(self.id_key_columns[x])
            if x != len(self.id_key_columns)-1:
                concat_policy.append(Value("-")) 
        first_id_key = self.id_key_columns[0]
        for data in obj_data_array:            
            if len(self.id_key_columns) > 1: 
                key = "-".join([(str(int(float(data[x]))) if data[x] else "")if x in self.int_key_columns else data[x] for x in self.id_key_columns ]) 
            else :
                key = int(float(data[first_id_key])) if self.int_key_columns else data[first_id_key]
            mapping[key] = data
        with transaction.atomic():
            if len(concat_policy)== 1:
                existing = {obj.__dict__[first_id_key] : obj for obj in  self.model.objects.filter(**{f"{first_id_key}__in" : mapping.keys()})}
            else:
                existing = {obj.unique_id:obj for obj in self.model.objects.annotate(unique_id = Concat(*concat_policy, output_field=CharField(max_length= 1024))).filter(unique_id__in = list(mapping.keys()))}
            create_objs = [
                self.model(**v) for k, v in mapping.items() if k not in existing
            ]
            created = self.model.objects.bulk_create(create_objs, ignore_conflicts= True)
            logger.info(f"{str(self.model)} Created : {len(created)}, Existing: {len(existing.keys())}")
            return {"created": len(created), "existing": len(existing.keys())}