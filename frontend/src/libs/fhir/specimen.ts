/**
 * FHIR Specimen resource builder.
 *
 * Maps BloodTrace BloodBag data to HL7 FHIR R4 Specimen resources.
 * See: https://www.hl7.org/fhir/specimen.html
 */

import type { BloodBag } from '../../types';

export interface FHIRSpecimen {
  resourceType: 'Specimen';
  id: string;
  identifier: Array<{
    system: string;
    value: string;
  }>;
  type: {
    coding: Array<{
      system: string;
      code: string;
      display: string;
    }>;
    text: string;
  };
  status?: string;
  collection?: {
    collectedDateTime: string;
  };
  container?: Array<{
    description: string;
    capacity: {
      value: number;
      unit: string;
    };
  }>;
}

const COMPONENT_SNOMED: Record<string, [string, string]> = {
  whole_blood: ['119297000', 'Blood specimen'],
  packed_rbc: ['708048008', 'Red blood cells unit'],
  plasma: ['119361006', 'Plasma specimen'],
  platelets: ['119305000', 'Platelet concentrate'],
  cryoprecipitate: ['708047003', 'Cryoprecipitate unit'],
};

const STATUS_MAP: Record<string, string> = {
  available: 'available',
  reserved: 'available',
  crossmatched: 'available',
  transfused: 'unavailable',
  expired: 'unavailable',
  discarded: 'unavailable',
  quarantine: 'unavailable',
};

export function buildFHIRSpecimen(params: {
  id: string;
  bloodType: string;
  rhFactor: string;
  component: string;
  volumeMl: number;
  collectionDate: string;
  status: string;
  storageLocation?: string;
}): FHIRSpecimen {
  const [snomedCode, snomedDisplay] = COMPONENT_SNOMED[params.component] || ['119297000', 'Blood specimen'];

  return {
    resourceType: 'Specimen',
    id: params.id,
    identifier: [{
      system: 'http://bloodtrace.local/fhir/identifier/blood-bag',
      value: params.id,
    }],
    type: {
      coding: [
        {
          system: 'http://snomed.info/sct',
          code: snomedCode,
          display: snomedDisplay,
        },
        {
          system: 'http://bloodtrace.local/fhir/blood-group',
          code: `${params.bloodType}${params.rhFactor}`,
          display: `Blood group ${params.bloodType}${params.rhFactor}`,
        },
      ],
      text: `${params.bloodType}${params.rhFactor} - ${params.component}`,
    },
    status: STATUS_MAP[params.status] || 'unavailable',
    collection: {
      collectedDateTime: params.collectionDate,
    },
    container: [{
      description: `Blood bag - ${params.component}${params.storageLocation ? ` at ${params.storageLocation}` : ''}`,
      capacity: {
        value: params.volumeMl,
        unit: 'mL',
      },
    }],
  };
}

export function buildFHIRSpecimenFromBloodBag(bag: BloodBag): FHIRSpecimen {
  return buildFHIRSpecimen({
    id: String(bag.id),
    bloodType: bag.blood_type,
    rhFactor: bag.rh_factor,
    component: bag.component,
    volumeMl: bag.volume_ml,
    collectionDate: bag.collection_date,
    status: bag.status,
    storageLocation: bag.storage_location,
  });
}
