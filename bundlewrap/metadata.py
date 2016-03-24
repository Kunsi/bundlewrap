from .exceptions import RepositoryError
from .utils import _Atomic, ATOMIC_TYPES, merge_dict
from .utils.text import mark_for_translation as _


def atomic(obj):
    try:
        cls = ATOMIC_TYPES[type(obj)]
    except KeyError:
        raise ValueError("atomic() can only be applied to dicts, lists, sets, or tuples "
                         "(not: {})".format(repr(obj)))
    else:
        return cls(obj)


def check_for_unsolvable_metadata_key_conflicts(node):
    """
    Finds metadata keys defined by two groups that are not part of a
    shared subgroup hierarchy.
    """
    # First, we build a list of subgroup chains.
    #
    # A chain is simply a list of groups starting with a parent group
    # that has no parent groups itself and then descends depth-first
    # into its subgroups until a subgroup is reached that the node is
    # not a member of.
    # Every possible path on every subgroup tree is a separate chain.
    #
    #      group4
    #     /     \
    #  group2  group3
    #     \     /
    #     group1
    #
    # This example has two chains, even though both start and end at the
    # some groups:
    #
    #     group1 -> group2 -> group4
    #     group1 -> group3 -> group4
    #

    # find all groups whose subgroups this node is *not* a member of
    lowest_subgroups = set()
    for group in node.groups:
        in_subgroup = False
        for subgroup in group.subgroups:
            if subgroup in node.groups:
                in_subgroup = True
                break
        if not in_subgroup:
            lowest_subgroups.add(group)

    chains = []
    incomplete_chains = [[group] for group in lowest_subgroups]

    while incomplete_chains:
        for chain in incomplete_chains[:]:
            highest_group = chain[-1]
            if list(highest_group.parent_groups):
                chain_so_far = chain[:]
                # continue this chain with the first parent group
                chain.append(list(highest_group.parent_groups)[0])
                # further parent groups form new chains
                for further_parents in list(highest_group.parent_groups)[1:]:
                    new_chain = chain_so_far[:]
                    new_chain.append(further_parents)
                    incomplete_chains.append(new_chain)
            else:
                # chain has ended
                chains.append(chain)
                incomplete_chains.remove(chain)

    # chains now look like this (parents right of children):
    # [
    #     [group1],
    #     [group2, group3, group5],
    #     [group2, group4, group5],
    #     [group2, group4, group6, group7],
    # ]

    # let's merge metadata for each chain
    chain_metadata = []
    for chain in chains:
        metadata = {}
        for group in chain:
            metadata = merge_dict(metadata, group.metadata)
        chain_metadata.append(metadata)

    # create a "key path map" for each chain's metadata
    chain_metadata_keys = [list(dictionary_key_map(metadata)) for metadata in chain_metadata]

    # compare all metadata keys with other chains and find matches
    for index1, keymap1 in enumerate(chain_metadata_keys):
        for keypath in keymap1:
            for index2, keymap2 in enumerate(chain_metadata_keys):
                if index1 == index2:
                    # same keymap, don't compare
                    continue
                else:
                    if keypath in keymap2:
                        # We now know that there is a conflict between the first
                        # and second chain we're looking at right now.
                        # That is however not a problem if the conflict is caused
                        # by a group that is present in both chains.
                        # So all that's left is to figure out which two single groups
                        # within those chains are at fault so we can report them
                        # to the user if necessary.
                        find_groups_causing_metadata_conflict(
                            node.name,
                            chains[index1],
                            chains[index2],
                        )


def dictionary_key_map(mapdict):
    """
    For the dict

        {
            "key1": 1,
            "key2": {
                "key3": 3,
                "key4": ["foo"],
             },
        }

    the key map would look like this:

        [
            ("key1",),
            ("key2", "key3"),
        ]

    Note that key4 is excluded because lists will be merged and do not
    overwrite each other (unless wrapped in atomic()).
    """
    for key, value in mapdict.items():
        if isinstance(value, dict):
            for child_keys in dictionary_key_map(value):
                yield (key,) + child_keys
        elif isinstance(value, (list, set, tuple)) and not isinstance(value, _Atomic):
            pass
        else:
            yield (key,)


def find_groups_causing_metadata_conflict(node_name, chain1, chain2):
    """
    Given two chains (lists of groups), find one group in each chain
    that has conflicting metadata with the other.
    """
    chain1_metadata = [list(dictionary_key_map(group.metadata)) for group in chain1]
    chain2_metadata = [list(dictionary_key_map(group.metadata)) for group in chain2]

    bad_keypath = None

    for index1, keymap1 in enumerate(chain1_metadata):
        for index2, keymap2 in enumerate(chain2_metadata):
            if chain1[index1] == chain2[index2]:
                # same group, ignore
                continue
            for keypath in keymap1:
                if keypath in keymap2:
                    bad_keypath = keypath
                    bad_group1 = chain1[index1]
                    bad_group2 = chain2[index2]

    if bad_keypath is not None:
        raise RepositoryError(_(
            "Conflicting metadata keys between groups '{group1}' and '{group2}' on node '{node}':\n\n"
            "    metadata['{keypath}']\n\n"
            "You must either connect both groups through subgroups or have them not define "
            "conflicting metadata keys. Otherwise there is no way for BundleWrap to determine "
            "which group's metadata should win when they are merged."
        ).format(
            keypath="']['".join(bad_keypath),
            group1=bad_group1.name,
            group2=bad_group2.name,
            node=node_name,
        ))
