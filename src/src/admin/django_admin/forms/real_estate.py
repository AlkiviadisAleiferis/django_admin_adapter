from django import forms
from django.core.exceptions import ValidationError
from backend.real_estate.models import (
    PropertyOwner,
    Agreement,
    AgreementParty,
)


class PropertyOwnerFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        total_ownership = 0

        forms_changed = 0

        # Agreement that can affect owners
        can_change_owners = self.instance.can_change_owners()

        for form in self.forms:
            if not form.cleaned_data.get("DELETE"):
                if form.cleaned_data.get("percentage"):
                    total_ownership += form.cleaned_data["percentage"]
                if form.has_changed():
                    forms_changed += 1

        if forms_changed and not can_change_owners:
            raise ValidationError(
                "Cannot change the owenership of a property with active Sales Agreement."
            )

        if total_ownership != 1 and total_ownership != 0:
            raise ValidationError("The asset's total ownership must be 100%")


class AgreementPartyFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        all_accepted = True
        agreement_cancelled = self.instance.status == Agreement.StatusChoices.CANCELLED

        total_owners_ownership_percent = 0
        total_buyers_ownership_percent = 0
        parties_num = 0
        owners = set()
        property_owners = set()
        parties_types = set()

        if self.instance.property is not None:
            property_owners_qs = PropertyOwner.objects.filter(
                property=self.instance.property
            )
            for owner in property_owners_qs:
                property_owners.add((owner.owner.id, owner.percentage))

        for form in self.forms:
            cleaned_data = form.cleaned_data
            if not cleaned_data.get("DELETE"):
                parties_num += 1
                parties_types.add(cleaned_data.get("party_type"))

                if not cleaned_data.get("accepted", False):
                    all_accepted = False

                if cleaned_data.get("percentage_ownership"):
                    party_type = cleaned_data.get("party_type")

                    if party_type in {
                        AgreementParty.PartyTypeChoices.SELLER,
                        AgreementParty.PartyTypeChoices.LANDLORD,
                    }:
                        party = cleaned_data["party"]
                        party_id = party if isinstance(party, int) else party.id
                        owners.add((party_id, cleaned_data["percentage_ownership"]))
                        total_owners_ownership_percent += cleaned_data[
                            "percentage_ownership"
                        ]

                    elif party_type == AgreementParty.PartyTypeChoices.BUYER:
                        total_buyers_ownership_percent += cleaned_data[
                            "percentage_ownership"
                        ]

        if not agreement_cancelled:
            # check if owners with corresponding percentages
            # are the same as the connected property's
            if property_owners != owners:
                raise ValidationError(
                    "Owning parties  (Sellers/Landlord) don't match owners of the property connected."
                )

            # check if all required parties are here
            # with respect to the agreement type
            if (
                self.instance.type == Agreement.TypeChoices.CONTRACT_OF_SALE
                and not parties_types.issuperset(
                    {
                        AgreementParty.PartyTypeChoices.BUYER,
                        AgreementParty.PartyTypeChoices.SELLER,
                    }
                )
            ):
                raise ValidationError(
                    "At least one Buyer and Seller parties must exist in a contract of sales."
                )
            elif (
                self.instance.type == Agreement.TypeChoices.PROPERTY_MANAGEMENT
                and not parties_types.issuperset(
                    {
                        AgreementParty.PartyTypeChoices.LANDLORD,
                        AgreementParty.PartyTypeChoices.MANAGER,
                    }
                )
            ):
                raise ValidationError(
                    "At least one Landlord and Manager parties must exist in a management contract."
                )
            elif (
                self.instance.type == Agreement.TypeChoices.TENANCY_AGREEMENT
                and not parties_types.issuperset(
                    {
                        AgreementParty.PartyTypeChoices.LANDLORD,
                        AgreementParty.PartyTypeChoices.TENANT,
                    }
                )
            ):
                raise ValidationError(
                    "At least one Landlord and Tenant parties must exist in a management contract."
                )

        # check total ownerships
        if total_owners_ownership_percent != 1 and total_owners_ownership_percent != 0:
            raise ValidationError(
                "The total ownership of landlords or sellers must be 100%."
            )
        if total_buyers_ownership_percent != 1 and total_buyers_ownership_percent != 0:
            raise ValidationError("The total ownership of buyers must be 100%.")

        # check accepted vs Agreement status
        if parties_num > 0:
            if (
                self.instance.status == Agreement.StatusChoices.AGREED
                and not all_accepted
            ):
                raise ValidationError(
                    "All signing parties must accept for the agreement to be complete."
                )
            elif self.instance.status != Agreement.StatusChoices.AGREED and all_accepted:
                raise ValidationError(
                    "All signing parties have accepted but agreement is not Agreed."
                )
        else:
            if self.instance.status == Agreement.StatusChoices.AGREED:
                raise ValidationError("Cannot be Agreed without signing parties.")
