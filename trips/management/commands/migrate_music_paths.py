"""
迁移音乐文件路径
将数据库中的 /static/music/ 路径改为 /music/
"""
from django.core.management.base import BaseCommand
from trips.models import Trip


class Command(BaseCommand):
    help = '迁移音乐文件路径：/static/music/ → /music/'

    def handle(self, *args, **options):
        self.stdout.write('开始迁移音乐文件路径...')
        
        # 查找所有包含 /static/music/ 的旅行
        trips = Trip.objects.filter(background_music__contains='/static/music/')
        count = trips.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('✅ 没有需要迁移的数据'))
            return
        
        self.stdout.write(f'找到 {count} 条需要迁移的记录')
        
        # 批量更新
        updated = 0
        for trip in trips:
            old_path = trip.background_music
            new_path = old_path.replace('/static/music/', '/music/')
            trip.background_music = new_path
            trip.save()
            updated += 1
            self.stdout.write(f'  [{updated}/{count}] {trip.title}: {old_path} → {new_path}')
        
        self.stdout.write(self.style.SUCCESS(f'✅ 成功迁移 {updated} 条记录'))

