from rest_framework import serializers

from teleband.musics.models import Piece, Part, PartTransposition, Composer, PartType

from teleband.musics.models import PartTransposition, EnsembleType
from teleband.instruments.models import Transposition
from teleband.utils.serializers import GenericNameSerializer


class ComposerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composer
        fields = ["name", "url"]


class PieceSerializer(serializers.ModelSerializer):
    composer = ComposerSerializer()

    class Meta:
        model = Piece
        fields = [
            "id",
            "name",
            "slug",
            "composer",
            "video",
            "audio",
            "date_composed",
            "ensemble_type",
            "accompaniment",
        ]


class TranspositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transposition
        fields = ["id", "name"]


class PartTranspositionSimpleSerializer(serializers.ModelSerializer):
    transposition = TranspositionSerializer()

    class Meta:
        model = PartTransposition
        fields = ["part", "transposition", "flatio"]


class PartSerializer(serializers.ModelSerializer):
    piece = PieceSerializer()
    transpositions = PartTranspositionSimpleSerializer(many=True)

    class Meta:
        model = Part
        fields = ["name", "piece", "transpositions"]


class PartTranspositionSerializer(serializers.ModelSerializer):
    part = PartSerializer()
    transposition = GenericNameSerializer()

    class Meta:
        model = PartTransposition
        fields = ["part", "transposition", "flatio", "sample_audio"]


class PartTranspositionCreateSerializer(serializers.ModelSerializer):
    transposition = GenericNameSerializer(model_cls=Transposition)

    class Meta:
        model = PartTransposition
        fields = ["transposition", "flatio"]

    def __init__(self, *args, **kwargs):
        self.part = kwargs.pop("part", None)
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        return PartTransposition.objects.create(part=self.part, **validated_data)


class PartCreateSerializer(serializers.ModelSerializer):
    transpositions = PartTranspositionCreateSerializer(many=True)
    part_type = GenericNameSerializer(model_cls=PartType)

    class Meta:
        model = Part
        fields = [
            "name",
            "part_type",
            "transpositions",
        ]

    def __init__(self, *args, **kwargs):
        self.piece = kwargs.pop("piece", None)
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        transpositions_data = validated_data.pop("transpositions")
        piece = Piece.objects.get(id=self.piece.id)
        # part = Part.objects.create(piece=self.piece, **validated_data)
        part = Part.objects.create(piece=piece, **validated_data)

        pts = PartTranspositionCreateSerializer(many=True, part=part)
        pts.create(transpositions_data)
        return part


class PieceCreateSerializer(serializers.ModelSerializer):
    parts = PartCreateSerializer(many=True)
    ensemble_type = GenericNameSerializer(model_cls=EnsembleType)
    # accompaniment = serializers.FilePathField(
    #     path="/Users/tgm/dev/CPR-Music-Backend/teleband/media/",
    #     recursive=True,
    #     required=False,
    #     allow_blank=True,
    #     allow_folders=True,
    #     allow_files=True
    # )
    # accompaniment = serializers.FileField(allow_empty_file=True, allow_null=True)
    accompaniment = serializers.CharField(allow_null=True, allow_blank=True)
    video = serializers.CharField(allow_null=True, allow_blank=True, required=False)

    class Meta:
        model = Piece
        fields = ["name", "ensemble_type", "parts", "accompaniment", "video"]

    def create(self, validated_data):
        print("\n\n\n\n")
        print(validated_data)
        print("\n\n\n\n")
        parts_data = validated_data.pop("parts")
        piece = Piece.objects.create(**validated_data)

        ps = PartCreateSerializer(many=True, piece=piece)
        ps.create(parts_data)
        return piece
